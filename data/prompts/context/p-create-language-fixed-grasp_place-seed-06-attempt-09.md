## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0676 | 0.29 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0602 | 0.16 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1530 | 0.25 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2716 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3370 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.068) — your mutation base

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
      distance: 0.1
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
      - 0.05
      - 0.2
      default: 0.1
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
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_retry_z: status=consumed; consumers=retry.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
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

- **Composite score**: 0.068
- **task_score** (E): 0.290
- **fitness_score**: 0.618  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1526 |
| descend_1 | 1.00 | 1.00 | 0.1079 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1031 |
| transport_1 | 0.33 | 1.00 | 0.1609 |
| place_descend_1 | 1.00 | 1.00 | 0.0922 |
| release_1 | 1.00 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.023, 0.152) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.023, 0.152)→(0.495, 0.024, 0.044) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.044)→(0.487, 0.023, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.147 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.036)→(0.483, 0.023, 0.139) | (0.500, 0.024, 0.026)→(0.497, 0.023, 0.120) | 0.272→0.223 | 1.00 / 24.000 | 0.103 | 0.556 |
| transport_1 | approach | 0.33 / step_budget | (0.483, 0.023, 0.139)→(0.567, 0.149, 0.178) | (0.497, 0.023, 0.120)→(0.558, 0.131, 0.092) | 0.223→0.140 | 1.00 / 14.333 | 91002.805 | 0.658 |
| place_descend_1 | descend | 1.00 / step_budget | (0.567, 0.149, 0.178)→(0.592, 0.191, 0.106) | (0.558, 0.131, 0.092)→(0.567, 0.152, 0.013) | 0.140→0.209 | 1.00 / 12.000 | 5.011 | 0.832 |
| release_1 | release | 1.00 / step_budget | (0.592, 0.191, 0.106)→(0.585, 0.189, 0.126) | (0.567, 0.152, 0.013)→(0.566, 0.148, 0.022) | 0.209→0.200 | 1.00 / 3.000 | 0.184 | 0.489 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.468
- phase_score: 0.628
- phase_breakdown.transport_arc_score: 0.636
- phase_breakdown.descend_1_score: 0.887
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.211
- phase_breakdown.release_1_score: 0.190
- grasp_place_fitness: 0.705

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.705
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.468
- **Median Q (composite search score)**: 0.038
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.268


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02381,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17188,"descend_1.grasp_z_offset":0.00111,"grasp_1.grasp_retry_x":-0.00695,"grasp_1.grasp_retry_y":-0.00048,"lift_1.lift_height":0.12367,"lift_1.lift_retry_z":0.01853,"place_descend_1.place_height":0.10532,"transport_1.transport_speed":0.19637},"optimized_scores":{"best_composite_score":0.01053,"best_fitness_score":0.56053,"best_task_score":0.16234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2508.0,"contact_point_centroid":[0.51392,0.06407,-0.00235],"force_p95":0.13227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50657,"mean_force":0.1422,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52974,0.07841,0.18343]},{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.50059,-0.01512,-0.0011],"force_p95":0.48414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68078,"mean_force":0.08781,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48935,-0.01532,0.02874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2880.0,"contact_point_centroid":[0.49931,0.02625,0.14389],"force_p95":0.1533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36003,"mean_force":0.1015,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49522,0.00814,0.14702]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10154.0,"contact_point_centroid":[0.48947,0.00361,0.07823],"force_p95":0.10823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3398,"mean_force":0.06933,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48673,-0.01528,0.07639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10925.0,"contact_point_centroid":[0.48957,-0.03405,0.07692],"force_p95":0.10334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30771,"mean_force":0.06517,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48674,-0.01528,0.07554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2754.0,"contact_point_centroid":[0.49881,-0.01201,0.14332],"force_p95":0.16224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25455,"mean_force":0.10125,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49436,0.00619,0.14612]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01552,-0.00203],"force_p95":0.13268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16192,"mean_force":0.12552,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49201,-0.01536,0.02827]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49926,-0.00636,0.25595]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49829,-0.01436,0.12217]},{"body_a":"world","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.51399,0.06422,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.56458,0.15124,0.16846]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51399,0.06422,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57545,0.17974,0.14081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4111.0,"contact_point_centroid":[0.49131,0.00386,0.02981],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11475,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01534,0.02704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4887.0,"contact_point_centroid":[0.49137,-0.03442,0.02889],"force_p95":0.06837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08842,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01534,0.02705]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2421.0,"contact_point_centroid":[0.53189,0.08207,0.18764],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53158,0.08206,0.18537]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1884.0,"contact_point_centroid":[0.56493,0.15119,0.17075],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01057,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.56456,0.15118,0.16852]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.57881,0.1808,0.13882],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01024,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57836,0.18079,0.13665]}],"total_contact_groups":16},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51399,0.06422,0.01602],"final_tcp_position":[0.57998,0.18107,0.13959],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273008.1618,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50011,-0.01333,0.21069],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49901,-0.01544,0.03571],"tcp_start":[0.50011,-0.01333,0.21069],"tcp_to_object_dist_end":0.01082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01521,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31207,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13027,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10798.0,"raw_peak_contact_force":0.16192,"subtask_id":"grasp_1","tcp_end":[0.49081,-0.01534,0.02701],"tcp_start":[0.49901,-0.01544,0.03571],"tcp_to_object_dist_end":0.01292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.50368,-0.01527,0.12599],"object_pos_start":[0.50368,-0.01521,0.02588],"object_to_goal_dist_end":0.25087,"object_to_goal_dist_start":0.31207,"object_z_max":0.12588,"peak_contact_force":0.11275,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21208.0,"raw_peak_contact_force":0.68078,"tcp_end":[0.48686,-0.01527,0.13882],"tcp_start":[0.49081,-0.01534,0.02701],"tcp_to_object_dist_end":0.02116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51399,0.06422,0.01602],"object_pos_start":[0.50368,-0.01527,0.12599],"object_to_goal_dist_end":0.27271,"object_to_goal_dist_start":0.25087,"object_z_max":0.13279,"peak_contact_force":273008.1618,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10563.0,"raw_peak_contact_force":1.50657,"subtask_id":"transport_arc","tcp_end":[0.55016,0.1192,0.20495],"tcp_start":[0.48686,-0.01527,0.13882],"tcp_to_object_dist_end":0.20006,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.51399,0.06422,0.01602],"object_pos_start":[0.51399,0.06422,0.01602],"object_to_goal_dist_end":0.27271,"object_to_goal_dist_start":0.27271,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3672.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57998,0.18107,0.13959],"tcp_start":[0.55016,0.1192,0.20495],"tcp_to_object_dist_end":0.18242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51399,0.06422,0.01602],"object_pos_start":[0.51399,0.06422,0.01602],"object_to_goal_dist_end":0.27271,"object_to_goal_dist_start":0.27271,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57372,0.17913,0.1607],"tcp_start":[0.57998,0.18107,0.13959],"tcp_to_object_dist_end":0.19417,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01587,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06973,"descend_1.grasp_z_offset":0.01334,"grasp_1.grasp_retry_x":0.00015,"grasp_1.grasp_retry_y":0.00459,"lift_1.lift_height":0.10838,"lift_1.lift_retry_z":0.01514,"place_descend_1.place_height":0.10666,"transport_1.transport_speed":0.24314},"optimized_scores":{"best_composite_score":0.15464,"best_fitness_score":0.70464,"best_task_score":0.46831},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":529.0,"contact_point_centroid":[0.60389,0.16963,-0.00982],"force_p95":1.11056,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22056,"mean_force":0.54934,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61499,0.16771,0.04105]},{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.6198,0.17107,-0.00766],"force_p95":1.06478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10845,"mean_force":0.66848,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61789,0.16724,0.05865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":612.0,"contact_point_centroid":[0.61808,0.18112,0.03576],"force_p95":0.34417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.61629,"mean_force":0.20076,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61728,0.16841,0.03962]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.50963,0.03703,-0.00122],"force_p95":0.35452,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50374,"mean_force":0.07399,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49737,0.03797,0.04052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.61563,0.14616,0.08768],"force_p95":0.20643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36093,"mean_force":0.12583,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61408,0.16347,0.09216]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9024.0,"contact_point_centroid":[0.49754,0.01891,0.08351],"force_p95":0.10455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31593,"mean_force":0.06786,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49484,0.03777,0.08151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9377.0,"contact_point_centroid":[0.49762,0.05664,0.08138],"force_p95":0.10379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31199,"mean_force":0.06631,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49488,0.03777,0.07962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2341.0,"contact_point_centroid":[0.6172,0.18054,0.08431],"force_p95":0.16795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2938,"mean_force":0.10774,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61435,0.16378,0.0891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1487.0,"contact_point_centroid":[0.61315,0.1437,0.03783],"force_p95":0.19101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26379,"mean_force":0.12214,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61442,0.16754,0.04216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13333.0,"contact_point_centroid":[0.55596,0.11675,0.13335],"force_p95":0.1144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24225,"mean_force":0.07178,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55121,0.09818,0.13316]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11449.0,"contact_point_centroid":[0.55665,0.08002,0.13329],"force_p95":0.12521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23346,"mean_force":0.08237,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55173,0.09872,0.13318]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03949,-0.00214],"force_p95":0.16211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22668,"mean_force":0.13307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50011,0.0382,0.03994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4076.0,"contact_point_centroid":[0.49965,0.0189,0.04144],"force_p95":0.0812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15357,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49894,0.03811,0.03866]},{"body_a":"world","body_b":"grasp_target","contact_count":2440.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50272,0.01811,0.20325]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50622,0.03766,0.0775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5013.0,"contact_point_centroid":[0.49962,0.05727,0.04046],"force_p95":0.07404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0792,"mean_force":0.04447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49895,0.03811,0.03867]}],"total_contact_groups":16},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61376,0.15649,0.03322],"final_tcp_position":[0.62007,0.16913,0.044],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":14.78742,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2440.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50762,0.03675,0.10765],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":780.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50705,0.03876,0.04766],"tcp_start":[0.50762,0.03675,0.10765],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03836,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21338,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15472,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10889.0,"raw_peak_contact_force":0.22668,"subtask_id":"grasp_1","tcp_end":[0.49891,0.0381,0.03863],"tcp_start":[0.50705,0.03876,0.04766],"tcp_to_object_dist_end":0.01884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50821,0.03794,0.11442],"object_pos_start":[0.51246,0.03836,0.02553],"object_to_goal_dist_end":0.18247,"object_to_goal_dist_start":0.21338,"object_z_max":0.11431,"peak_contact_force":0.0984,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18542.0,"raw_peak_contact_force":0.50374,"tcp_end":[0.49491,0.03778,0.13501],"tcp_start":[0.49891,0.0381,0.03863],"tcp_to_object_dist_end":0.02451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61558,0.16023,0.10182],"object_pos_start":[0.50821,0.03794,0.11442],"object_to_goal_dist_end":0.04649,"object_to_goal_dist_start":0.18247,"object_z_max":0.11445,"peak_contact_force":0.12711,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24782.0,"raw_peak_contact_force":0.24225,"subtask_id":"transport_arc","tcp_end":[0.61161,0.15949,0.13575],"tcp_start":[0.49491,0.03778,0.13501],"tcp_to_object_dist_end":0.03417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.61842,0.16795,0.00683],"object_pos_start":[0.61558,0.16023,0.10182],"object_to_goal_dist_end":0.13858,"object_to_goal_dist_start":0.04649,"object_z_max":0.10182,"peak_contact_force":14.78742,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4367.0,"raw_peak_contact_force":1.10845,"tcp_end":[0.62007,0.16913,0.044],"tcp_start":[0.61161,0.15949,0.13575],"tcp_to_object_dist_end":0.03723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61376,0.15649,0.03322],"object_pos_start":[0.61842,0.16795,0.00683],"object_to_goal_dist_end":0.11379,"object_to_goal_dist_start":0.13858,"object_z_max":0.0334,"peak_contact_force":0.30619,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2628.0,"raw_peak_contact_force":1.22056,"subtask_id":"release_1","tcp_end":[0.61173,0.16673,0.06364],"tcp_start":[0.62007,0.16913,0.044],"tcp_to_object_dist_end":0.03216,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02479,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09957,"descend_1.grasp_z_offset":0.01498,"grasp_1.grasp_retry_x":-0.00153,"grasp_1.grasp_retry_y":-0.00219,"lift_1.lift_height":0.11232,"lift_1.lift_retry_z":0.01292,"place_descend_1.place_height":0.09267,"transport_1.transport_speed":0.17924},"optimized_scores":{"best_composite_score":0.03775,"best_fitness_score":0.58775,"best_task_score":0.23869},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":805.0,"contact_point_centroid":[0.56965,0.22311,-0.00311],"force_p95":0.57058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26541,"mean_force":0.16732,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.56773,0.21237,0.14407]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.48006,0.04586,-0.00121],"force_p95":0.30382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48199,"mean_force":0.06793,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4689,0.0468,0.04353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10346.0,"contact_point_centroid":[0.46848,0.06557,0.08641],"force_p95":0.10422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30521,"mean_force":0.06339,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4665,0.04658,0.08457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10245.0,"contact_point_centroid":[0.46877,0.02771,0.08877],"force_p95":0.09939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27305,"mean_force":0.06295,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46649,0.04658,0.08693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1533.0,"contact_point_centroid":[0.55282,0.16223,0.172],"force_p95":0.16536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24203,"mean_force":0.11524,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54701,0.18045,0.17701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1757.0,"contact_point_centroid":[0.55253,0.1987,0.17158],"force_p95":0.12635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23279,"mean_force":0.09941,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54724,0.18079,0.17667]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04856,-0.00215],"force_p95":0.16313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22799,"mean_force":0.13349,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47148,0.04707,0.04274]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10388.0,"contact_point_centroid":[0.5062,0.08663,0.16568],"force_p95":0.13364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22496,"mean_force":0.0885,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50062,0.10516,0.16572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11138.0,"contact_point_centroid":[0.50632,0.12339,0.16534],"force_p95":0.12383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19714,"mean_force":0.08351,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5005,0.10499,0.16563]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48941,0.02175,0.21898]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47808,0.04599,0.09356]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56965,0.22312,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57041,0.22139,0.13469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5042.0,"contact_point_centroid":[0.47015,0.02771,0.04444],"force_p95":0.06998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11797,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47038,0.04696,0.04161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5528.0,"contact_point_centroid":[0.46998,0.06628,0.04385],"force_p95":0.07021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07287,"mean_force":0.04084,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47038,0.04696,0.04161]},{"body_a":"left_finger","body_b":"right_finger","contact_count":518.0,"contact_point_centroid":[0.57107,0.21667,0.14216],"force_p95":0.01373,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01473,"mean_force":0.01106,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57062,0.21664,0.13994]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.5737,0.22267,0.13253],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01104,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5733,0.22264,0.13066]}],"total_contact_groups":16},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56965,0.22312,0.01602],"final_tcp_position":[0.57489,0.22311,0.13364],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.26541,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48039,0.0445,0.13811],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47812,0.04772,0.04965],"tcp_start":[0.48039,0.0445,0.13811],"tcp_to_object_dist_end":0.02409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48266,0.04745,0.02549],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29116,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1574,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12370.0,"raw_peak_contact_force":0.22799,"subtask_id":"grasp_1","tcp_end":[0.47035,0.04696,0.04158],"tcp_start":[0.47812,0.04772,0.04965],"tcp_to_object_dist_end":0.02026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.47924,0.04693,0.11945],"object_pos_start":[0.48266,0.04745,0.02549],"object_to_goal_dist_end":0.23655,"object_to_goal_dist_start":0.29116,"object_z_max":0.11934,"peak_contact_force":0.09909,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20728.0,"raw_peak_contact_force":0.48199,"tcp_end":[0.46653,0.04659,0.14248],"tcp_start":[0.47035,0.04696,0.04158],"tcp_to_object_dist_end":0.0263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5454,0.16844,0.15783],"object_pos_start":[0.47924,0.04693,0.11945],"object_to_goal_dist_end":0.10128,"object_to_goal_dist_start":0.23655,"object_z_max":0.15781,"peak_contact_force":0.12531,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21526.0,"raw_peak_contact_force":0.22496,"subtask_id":"transport_arc","tcp_end":[0.54045,0.16789,0.19471],"tcp_start":[0.46653,0.04659,0.14248],"tcp_to_object_dist_end":0.03721,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.56965,0.22312,0.01602],"object_pos_start":[0.5454,0.16844,0.15783],"object_to_goal_dist_end":0.21489,"object_to_goal_dist_start":0.10128,"object_z_max":0.15783,"peak_contact_force":0.12261,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4613.0,"raw_peak_contact_force":1.26541,"tcp_end":[0.57489,0.22311,0.13364],"tcp_start":[0.54045,0.16789,0.19471],"tcp_to_object_dist_end":0.11774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56965,0.22312,0.01602],"object_pos_start":[0.56965,0.22312,0.01602],"object_to_goal_dist_end":0.21489,"object_to_goal_dist_start":0.21489,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.56869,0.22063,0.15448],"tcp_start":[0.57489,0.22311,0.13364],"tcp_to_object_dist_end":0.13849,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```