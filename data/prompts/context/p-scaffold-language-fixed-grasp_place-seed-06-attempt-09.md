## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0408 | 0.24 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0357 | 0.42 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0750 | 0.30 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0057 | 0.26 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0328 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.041) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
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
      distance: 0.2
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
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.041
- **task_score** (E): 0.235
- **fitness_score**: 0.591  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1291 |
| descend_1 | 1.00 | 1.00 | 0.1329 |
| grasp_1 | 1.00 | 1.00 | 0.0115 |
| lift_1 | 0.00 | 1.00 | 0.1397 |
| transport_arc | 1.00 | 1.00 | 0.2594 |
| place_descend | 1.00 | 1.00 | 0.1251 |
| release | 1.00 | 1.00 | 0.0151 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.176) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.176)→(0.495, 0.024, 0.044) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.044)→(0.487, 0.023, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 45.000 | 0.143 | 0.205 |
| lift_1 | lift | 0.00 / step_budget | (0.487, 0.023, 0.035)→(0.483, 0.023, 0.175) | (0.500, 0.023, 0.026)→(0.493, 0.023, 0.154) | 0.272→0.212 | 1.00 / 24.333 | 0.145 | 0.568 |
| transport_arc | approach | 1.00 / step_budget | (0.483, 0.023, 0.175)→(0.592, 0.188, 0.341) | (0.493, 0.023, 0.154)→(0.536, 0.081, 0.016) | 0.212→0.238 | 1.00 / 8.000 | 0.123 | 2.022 |
| place_descend | descend | 1.00 / step_budget | (0.592, 0.188, 0.341)→(0.595, 0.194, 0.217) | (0.536, 0.081, 0.016)→(0.536, 0.081, 0.016) | 0.238→0.238 | 1.00 / 8.667 | 94251.669 | 0.123 |
| release | grasp | 1.00 / step_budget | (0.595, 0.194, 0.217)→(0.589, 0.192, 0.203) | (0.536, 0.081, 0.016)→(0.536, 0.081, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.417
- phase_score: 0.387
- phase_breakdown.descend_1_score: 0.719
- phase_breakdown.transport_arc_score: 0.069
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.079
- phase_breakdown.release_1_score: 0.823
- grasp_place_fitness: 0.688

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.688
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.417
- **Median Q (composite search score)**: 0.007
- **K-run variance**: 0.0048
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38488,"average_solve_count":291.0,"average_success_count":291.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16762,"approach_1.speed":0.06214,"descend_1.grasp_z_offset":0.02582,"descend_1.speed":0.04454,"lift_1.lift_height":0.30836,"lift_1.speed":0.1009,"place_descend.speed":0.03906,"transport_arc.speed":0.07751},"optimized_scores":{"best_composite_score":-0.02275,"best_fitness_score":0.52725,"best_task_score":0.12392},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3209.0,"contact_point_centroid":[0.50632,-0.00685,-0.00234],"force_p95":0.12522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92577,"mean_force":0.13685,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53958,0.09484,0.30488]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.50104,-0.0156,-0.0011],"force_p95":0.3196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44838,"mean_force":0.06444,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48967,-0.01539,0.04614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14526.0,"contact_point_centroid":[0.49048,0.00359,0.11372],"force_p95":0.11096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33484,"mean_force":0.06905,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48722,-0.01534,0.11174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15774.0,"contact_point_centroid":[0.49044,-0.03417,0.11652],"force_p95":0.0991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28731,"mean_force":0.06431,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48719,-0.01534,0.11464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.49403,-0.03008,0.20429],"force_p95":0.18316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2514,"mean_force":0.0886,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.488,-0.01365,0.20877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":58.0,"contact_point_centroid":[0.49406,0.00321,0.20231],"force_p95":0.20213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24281,"mean_force":0.14977,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4877,-0.01474,0.20814]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01562,-0.00203],"force_p95":0.13033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1573,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49229,-0.01542,0.04568]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.50382,-0.01567,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49909,-0.0064,0.25379]},{"body_a":"world","body_b":"grasp_target","contact_count":3704.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49799,-0.01449,0.12471]},{"body_a":"world","body_b":"grasp_target","contact_count":1424.0,"contact_point_centroid":[0.5063,-0.00682,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58198,0.18114,0.32037]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5063,-0.00682,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"grasp","tcp_position_centroid":[0.58026,0.18407,0.24788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5452.0,"contact_point_centroid":[0.49021,0.00379,0.04825],"force_p95":0.06462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09103,"mean_force":0.04024,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49114,-0.01541,0.04443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5026.0,"contact_point_centroid":[0.4906,-0.03469,0.04752],"force_p95":0.06825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08162,"mean_force":0.04379,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49114,-0.01541,0.04444]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3226.0,"contact_point_centroid":[0.54276,0.10078,0.31259],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01044,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54254,0.10078,0.31037]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1524.0,"contact_point_centroid":[0.58236,0.18117,0.32224],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01042,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58199,0.18116,0.32003]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.58291,0.18485,0.25548],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release","phase_type":"grasp","tcp_position_centroid":[0.58232,0.18484,0.25349]}],"total_contact_groups":16},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5063,-0.00682,0.01602],"final_tcp_position":[0.58363,0.18525,0.2571],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9749.03773,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49998,-0.01343,0.20638],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3704.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49896,-0.01551,0.05295],"tcp_start":[0.49998,-0.01343,0.20638],"tcp_to_object_dist_end":0.02736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.0156,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31232,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12942,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12278.0,"raw_peak_contact_force":0.1573,"subtask_id":"grasp_1","tcp_end":[0.49111,-0.0154,0.0444],"tcp_start":[0.49896,-0.01551,0.05295],"tcp_to_object_dist_end":0.02242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49646,-0.01506,0.17844],"object_pos_start":[0.50373,-0.0156,0.02587],"object_to_goal_dist_end":0.23248,"object_to_goal_dist_start":0.31232,"object_z_max":0.17827,"peak_contact_force":0.21026,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30430.0,"raw_peak_contact_force":0.44838,"tcp_end":[0.48758,-0.01534,0.20762],"tcp_start":[0.49111,-0.0154,0.0444],"tcp_to_object_dist_end":0.0305,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.5063,-0.00682,0.01602],"object_pos_start":[0.49646,-0.01506,0.17844],"object_to_goal_dist_end":0.31322,"object_to_goal_dist_start":0.23248,"object_z_max":0.17853,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6645.0,"raw_peak_contact_force":1.92577,"subtask_id":"transport_arc","tcp_end":[0.58123,0.17773,0.38162],"tcp_start":[0.48758,-0.01534,0.20762],"tcp_to_object_dist_end":0.41634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.5063,-0.00682,0.01602],"object_pos_start":[0.5063,-0.00682,0.01602],"object_to_goal_dist_end":0.31322,"object_to_goal_dist_start":0.31322,"object_z_max":0.01602,"peak_contact_force":9749.03773,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2948.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58363,0.18525,0.2571],"tcp_start":[0.58123,0.17773,0.38162],"tcp_to_object_dist_end":0.31779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5063,-0.00682,0.01602],"object_pos_start":[0.5063,-0.00682,0.01602],"object_to_goal_dist_end":0.31322,"object_to_goal_dist_start":0.31322,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57874,0.18352,0.24379],"tcp_start":[0.58363,0.18525,0.2571],"tcp_to_object_dist_end":0.30554,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32016,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11896,"approach_1.speed":0.0327,"descend_1.grasp_z_offset":0.01137,"descend_1.speed":0.07006,"lift_1.lift_height":0.20822,"lift_1.speed":0.05869,"place_descend.speed":0.0627,"transport_arc.speed":0.14565},"optimized_scores":{"best_composite_score":0.13767,"best_fitness_score":0.68767,"best_task_score":0.41666},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":487.0,"contact_point_centroid":[0.60535,0.16288,-0.00458],"force_p95":0.93962,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1076,"mean_force":0.2266,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.6096,0.15584,0.26652]},{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.50783,0.03776,-0.00121],"force_p95":0.47826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69432,"mean_force":0.10888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49763,0.03841,0.02734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19779.0,"contact_point_centroid":[0.49553,0.05733,0.07571],"force_p95":0.07594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32069,"mean_force":0.05179,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49516,0.03821,0.07394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6643.0,"contact_point_centroid":[0.53426,0.05814,0.16715],"force_p95":0.1434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31211,"mean_force":0.07967,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53076,0.07679,0.16725]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19530.0,"contact_point_centroid":[0.49554,0.01909,0.07792],"force_p95":0.0773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30982,"mean_force":0.0518,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49516,0.03821,0.07585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6938.0,"contact_point_centroid":[0.5374,0.09872,0.17083],"force_p95":0.13898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27651,"mean_force":0.07795,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53396,0.08003,0.17129]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03942,-0.0021],"force_p95":0.15349,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22903,"mean_force":0.13101,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50068,0.03867,0.02695]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50261,0.0175,0.22823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4064.0,"contact_point_centroid":[0.5,0.01937,0.02846],"force_p95":0.07987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13695,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49947,0.03857,0.02565]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.6051,0.16262,-0.00199],"force_p95":0.12328,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12478,"mean_force":0.12269,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62002,0.16758,0.21639]},{"body_a":"world","body_b":"grasp_target","contact_count":3452.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50614,0.03775,0.08464]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6051,0.16262,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"grasp","tcp_position_centroid":[0.61773,0.16899,0.14304]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4973.0,"contact_point_centroid":[0.5,0.05771,0.02747],"force_p95":0.07223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0885,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49948,0.03857,0.02566]},{"body_a":"left_finger","body_b":"right_finger","contact_count":331.0,"contact_point_centroid":[0.61371,0.15931,0.27316],"force_p95":0.01445,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01781,"mean_force":0.01129,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.61306,0.15929,0.27085]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1456.0,"contact_point_centroid":[0.6205,0.16761,0.21853],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01047,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62002,0.16758,0.2163]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62136,0.16994,0.15153],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release","phase_type":"grasp","tcp_position_centroid":[0.62075,0.1699,0.14919]}],"total_contact_groups":16},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6051,0.16262,0.01602],"final_tcp_position":[0.62266,0.17044,0.15317],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":2.1076,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50764,0.03597,0.15655],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3452.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50748,0.03923,0.03432],"tcp_start":[0.50764,0.03597,0.15655],"tcp_to_object_dist_end":0.00972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.03851,0.02565],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21325,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1463,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10837.0,"raw_peak_contact_force":0.22903,"subtask_id":"grasp_1","tcp_end":[0.49945,0.03856,0.02562],"tcp_start":[0.50748,0.03923,0.03432],"tcp_to_object_dist_end":0.01294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50544,0.03823,0.11339],"object_pos_start":[0.51238,0.03851,0.02565],"object_to_goal_dist_end":0.18426,"object_to_goal_dist_start":0.21325,"object_z_max":0.11329,"peak_contact_force":0.06977,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39499.0,"raw_peak_contact_force":0.69432,"tcp_end":[0.49524,0.03823,0.12251],"tcp_start":[0.49945,0.03856,0.02562],"tcp_to_object_dist_end":0.01368,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.6051,0.1627,0.01604],"object_pos_start":[0.50544,0.03823,0.11339],"object_to_goal_dist_end":0.13129,"object_to_goal_dist_start":0.18426,"object_z_max":0.20892,"peak_contact_force":0.12493,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14399.0,"raw_peak_contact_force":2.1076,"subtask_id":"transport_arc","tcp_end":[0.61919,0.16545,0.27851],"tcp_start":[0.49524,0.03823,0.12251],"tcp_to_object_dist_end":0.26286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.6051,0.16262,0.01602],"object_pos_start":[0.6051,0.1627,0.01604],"object_to_goal_dist_end":0.13132,"object_to_goal_dist_start":0.13129,"object_z_max":0.01604,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2824.0,"raw_peak_contact_force":0.12478,"subtask_id":"release_1","tcp_end":[0.62266,0.17044,0.15317],"tcp_start":[0.61919,0.16545,0.27851],"tcp_to_object_dist_end":0.13849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6051,0.16262,0.01602],"object_pos_start":[0.6051,0.16262,0.01602],"object_to_goal_dist_end":0.13132,"object_to_goal_dist_start":0.13132,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61552,0.16832,0.13858],"tcp_start":[0.62266,0.17044,0.15317],"tcp_to_object_dist_end":0.12313,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01929,"average_solve_count":311.0,"average_success_count":311.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12775,"approach_1.speed":0.05886,"descend_1.grasp_z_offset":0.01572,"descend_1.speed":0.02247,"lift_1.lift_height":0.33835,"lift_1.speed":0.09748,"place_descend.speed":0.0517,"transport_arc.speed":0.10497},"optimized_scores":{"best_composite_score":0.00746,"best_fitness_score":0.55746,"best_task_score":0.16468},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2816.0,"contact_point_centroid":[0.49649,0.08774,-0.00237],"force_p95":0.12515,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03118,"mean_force":0.13912,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53015,0.15,0.29391]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.47993,0.04643,-0.00118],"force_p95":0.37392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56147,"mean_force":0.07553,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4689,0.04711,0.0373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14199.0,"contact_point_centroid":[0.46946,0.06574,0.10223],"force_p95":0.11329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31141,"mean_force":0.07081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46651,0.04688,0.10084]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14028.0,"contact_point_centroid":[0.46971,0.02813,0.10389],"force_p95":0.11577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28522,"mean_force":0.0708,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4665,0.04688,0.10246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":497.0,"contact_point_centroid":[0.47538,0.07144,0.19465],"force_p95":0.16938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26105,"mean_force":0.10531,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47002,0.05391,0.19966]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":369.0,"contact_point_centroid":[0.47447,0.03394,0.19323],"force_p95":0.21651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25814,"mean_force":0.14266,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46898,0.05183,0.19802]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04853,-0.00213],"force_p95":0.15824,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2289,"mean_force":0.13223,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47151,0.04737,0.03657]},{"body_a":"world","body_b":"grasp_target","contact_count":1864.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48963,0.02124,0.23316]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.47017,0.02802,0.03826],"force_p95":0.06916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12543,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47039,0.04726,0.03542]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47774,0.04585,0.10104]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.49646,0.08774,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57641,0.22261,0.3026]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49646,0.08774,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"grasp","tcp_position_centroid":[0.57484,0.22493,0.22992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5497.0,"contact_point_centroid":[0.46999,0.06657,0.03766],"force_p95":0.06921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07731,"mean_force":0.04103,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47039,0.04726,0.03542]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2762.0,"contact_point_centroid":[0.53382,0.15504,0.30118],"force_p95":0.01117,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53339,0.15502,0.29897]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1511.0,"contact_point_centroid":[0.57687,0.22263,0.30482],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01042,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57641,0.22261,0.30262]},{"body_a":"left_finger","body_b":"right_finger","contact_count":230.0,"contact_point_centroid":[0.57744,0.22593,0.23802],"force_p95":0.01085,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00975,"phase_index":6.0,"phase_name":"release","phase_type":"grasp","tcp_position_centroid":[0.577,0.22589,0.23566]}],"total_contact_groups":16},"final_pose_error":0.0098,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.49646,0.08774,0.01602],"final_tcp_position":[0.57836,0.22643,0.23931],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273005.84703,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48077,0.04382,0.16602],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47801,0.04802,0.04325],"tcp_start":[0.48077,0.04382,0.16602],"tcp_to_object_dist_end":0.01787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48263,0.04755,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29106,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15285,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12333.0,"raw_peak_contact_force":0.2289,"subtask_id":"grasp_1","tcp_end":[0.47036,0.04726,0.03539],"tcp_start":[0.47801,0.04802,0.04325],"tcp_to_object_dist_end":0.01573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47604,0.04723,0.17036],"object_pos_start":[0.48263,0.04755,0.02556],"object_to_goal_dist_end":0.21863,"object_to_goal_dist_start":0.29106,"object_z_max":0.17019,"peak_contact_force":0.15547,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28364.0,"raw_peak_contact_force":0.56147,"tcp_end":[0.46679,0.04691,0.19426],"tcp_start":[0.47036,0.04726,0.03539],"tcp_to_object_dist_end":0.02563,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.49646,0.08774,0.01602],"object_pos_start":[0.47604,0.04723,0.17036],"object_to_goal_dist_end":0.27056,"object_to_goal_dist_start":0.21863,"object_z_max":0.17763,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6444.0,"raw_peak_contact_force":2.03118,"subtask_id":"transport_arc","tcp_end":[0.57535,0.21952,0.3642],"tcp_start":[0.46679,0.04691,0.19426],"tcp_to_object_dist_end":0.38056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.49646,0.08774,0.01602],"object_pos_start":[0.49646,0.08774,0.01602],"object_to_goal_dist_end":0.27056,"object_to_goal_dist_start":0.27056,"object_z_max":0.01602,"peak_contact_force":273005.84703,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2923.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57836,0.22643,0.23931],"tcp_start":[0.57535,0.21952,0.3642],"tcp_to_object_dist_end":0.27532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49646,0.08774,0.01602],"object_pos_start":[0.49646,0.08774,0.01602],"object_to_goal_dist_end":0.27056,"object_to_goal_dist_start":0.27056,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1030.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57326,0.22423,0.22575],"tcp_start":[0.57836,0.22643,0.23931],"tcp_to_object_dist_end":0.26176,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```