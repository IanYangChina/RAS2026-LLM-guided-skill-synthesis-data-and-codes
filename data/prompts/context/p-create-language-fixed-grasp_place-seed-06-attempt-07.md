## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1530 | 0.25 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2716 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3370 | 0.22 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0981 | 0.21 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1049 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.153) — your mutation base

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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
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
  termination: time_limit
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
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
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

- **Composite score**: 0.153
- **task_score** (E): 0.254
- **fitness_score**: 0.603  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1069 |
| descend_1 | 1.00 | 1.00 | 0.1588 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.0961 |
| transport_1 | 0.67 | 1.00 | 0.1912 |
| place_descend_1 | 1.00 | 1.00 | 0.0860 |
| release_1 | 1.00 | 1.00 | 0.0215 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.021, 0.200) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.021, 0.200)→(0.495, 0.024, 0.041) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.041)→(0.487, 0.023, 0.033) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.147 | 0.210 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.033)→(0.483, 0.023, 0.129) | (0.500, 0.023, 0.026)→(0.498, 0.023, 0.113) | 0.272→0.226 | 1.00 / 24.333 | 0.071 | 0.594 |
| transport_1 | approach | 0.67 / step_budget | (0.483, 0.023, 0.129)→(0.575, 0.162, 0.208) | (0.498, 0.023, 0.113)→(0.538, 0.095, 0.048) | 0.226→0.199 | 1.00 / 11.333 | 0.125 | 1.261 |
| place_descend_1 | descend | 1.00 / step_budget | (0.575, 0.162, 0.208)→(0.591, 0.191, 0.130) | (0.538, 0.095, 0.048)→(0.542, 0.099, 0.018) | 0.199→0.227 | 1.00 / 11.000 | 0.292 | 0.292 |
| release_1 | release | 1.00 / step_budget | (0.591, 0.191, 0.130)→(0.585, 0.188, 0.150) | (0.542, 0.099, 0.018)→(0.536, 0.099, 0.019) | 0.227→0.226 | 1.00 / 4.000 | 0.123 | 0.320 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.588
- phase_breakdown.transport_arc_score: 0.562
- phase_breakdown.descend_1_score: 0.898
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.031
- phase_breakdown.release_1_score: 0.249
- grasp_place_fitness: 0.694

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.694
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: 0.115
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.384


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02419,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14125,"descend_1.grasp_z_offset":0.00378,"lift_1.lift_height":0.10709,"place_descend_1.place_height":0.07845,"transport_1.arc_height":0.27723,"transport_1.transport_speed":0.25302},"optimized_scores":{"best_composite_score":0.10071,"best_fitness_score":0.55071,"best_task_score":0.1444},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2489.0,"contact_point_centroid":[0.49824,0.03751,-0.00234],"force_p95":0.14634,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81958,"mean_force":0.14296,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52722,0.07228,0.2335]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.50072,-0.01514,-0.00109],"force_p95":0.47247,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62828,"mean_force":0.08261,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48932,-0.01533,0.03156]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2781.0,"contact_point_centroid":[0.49379,0.01221,0.14855],"force_p95":0.16887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37652,"mean_force":0.10656,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4882,-0.00611,0.14963]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9287.0,"contact_point_centroid":[0.48919,0.00361,0.07422],"force_p95":0.10458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33712,"mean_force":0.06635,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48671,-0.01528,0.07239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9870.0,"contact_point_centroid":[0.48908,-0.03413,0.07291],"force_p95":0.10256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30385,"mean_force":0.06318,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48673,-0.01528,0.07134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2795.0,"contact_point_centroid":[0.4934,-0.02549,0.14649],"force_p95":0.16265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26577,"mean_force":0.09971,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48779,-0.00712,0.14726]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01553,-0.00203],"force_p95":0.13276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15973,"mean_force":0.12552,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49199,-0.01536,0.03107]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49909,-0.00669,0.24049]},{"body_a":"world","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49815,-0.01462,0.10866]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.49807,0.03746,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.56746,0.15592,0.20904]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49807,0.03746,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57575,0.1792,0.17153]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.4913,0.00385,0.03261],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11744,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49082,-0.01535,0.02985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.49136,-0.03443,0.03169],"force_p95":0.06844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08971,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49083,-0.01535,0.02985]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2455.0,"contact_point_centroid":[0.52955,0.07634,0.23832],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01561,"mean_force":0.01053,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52926,0.07633,0.23621]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1518.0,"contact_point_centroid":[0.56783,0.1558,0.21139],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01048,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5674,0.15579,0.20925]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.57861,0.18018,0.16955],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01105,"mean_force":0.01024,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57834,0.18017,0.16731]}],"total_contact_groups":16},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49807,0.03746,0.01602],"final_tcp_position":[0.57999,0.18043,0.17048],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.81958,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49996,-0.01387,0.18011],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1772.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49896,-0.01544,0.03852],"tcp_start":[0.49996,-0.01387,0.18011],"tcp_to_object_dist_end":0.01341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01522,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13046,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15973,"subtask_id":"grasp_1","tcp_end":[0.49079,-0.01535,0.02982],"tcp_start":[0.49896,-0.01544,0.03852],"tcp_to_object_dist_end":0.01348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50282,-0.01514,0.11225],"object_pos_start":[0.50369,-0.01522,0.02587],"object_to_goal_dist_end":0.25801,"object_to_goal_dist_start":0.31208,"object_z_max":0.11215,"peak_contact_force":0.11348,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19290.0,"raw_peak_contact_force":0.62828,"tcp_end":[0.48674,-0.01528,0.12519],"tcp_start":[0.49079,-0.01535,0.02982],"tcp_to_object_dist_end":0.02064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49807,0.03746,0.01602],"object_pos_start":[0.50282,-0.01514,0.11225],"object_to_goal_dist_end":0.29027,"object_to_goal_dist_start":0.25801,"object_z_max":0.15435,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10520.0,"raw_peak_contact_force":1.81958,"subtask_id":"transport_arc","tcp_end":[0.55687,0.13204,0.25217],"tcp_start":[0.48674,-0.01528,0.12519],"tcp_to_object_dist_end":0.26109,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.49807,0.03746,0.01602],"object_pos_start":[0.49807,0.03746,0.01602],"object_to_goal_dist_end":0.29027,"object_to_goal_dist_start":0.29027,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2946.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57999,0.18043,0.17048],"tcp_start":[0.55687,0.13204,0.25217],"tcp_to_object_dist_end":0.22586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49807,0.03746,0.01602],"object_pos_start":[0.49807,0.03746,0.01602],"object_to_goal_dist_end":0.29027,"object_to_goal_dist_start":0.29027,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5742,0.17863,0.19142],"tcp_start":[0.57999,0.18043,0.17048],"tcp_to_object_dist_end":0.23768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02479,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16713,"descend_1.grasp_z_offset":0.01343,"lift_1.lift_height":0.10765,"place_descend_1.place_height":0.09084,"transport_1.arc_height":0.36042,"transport_1.transport_speed":0.19621},"optimized_scores":{"best_composite_score":0.2437,"best_fitness_score":0.6937,"best_task_score":0.44573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":686.0,"contact_point_centroid":[0.60904,0.16686,-0.00397],"force_p95":0.65677,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71564,"mean_force":0.23193,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61333,0.16675,0.0589]},{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.62249,0.16602,-0.00388],"force_p95":0.60974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63182,"mean_force":0.41643,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61783,0.16691,0.06608]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.50974,0.03725,-0.0012],"force_p95":0.36351,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50676,"mean_force":0.07307,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49792,0.03813,0.04079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":483.0,"contact_point_centroid":[0.62122,0.18601,0.04838],"force_p95":0.15439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42908,"mean_force":0.1286,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61674,0.16778,0.05372]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.621,0.14966,0.04897],"force_p95":0.12867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33136,"mean_force":0.09613,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61683,0.1678,0.05384]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2364.0,"contact_point_centroid":[0.61536,0.14212,0.09792],"force_p95":0.15635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33001,"mean_force":0.11289,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61111,0.16034,0.10216]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9500.0,"contact_point_centroid":[0.49789,0.01907,0.08372],"force_p95":0.10077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3202,"mean_force":0.06463,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4954,0.03793,0.08193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9805.0,"contact_point_centroid":[0.49754,0.05687,0.08128],"force_p95":0.1041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31119,"mean_force":0.06345,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49543,0.03793,0.07951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2353.0,"contact_point_centroid":[0.61547,0.17829,0.09779],"force_p95":0.14537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2986,"mean_force":0.11035,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61098,0.16024,0.10257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11551.0,"contact_point_centroid":[0.55266,0.11161,0.15127],"force_p95":0.12254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24684,"mean_force":0.08155,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54671,0.09323,0.15114]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10201.0,"contact_point_centroid":[0.55335,0.07571,0.15206],"force_p95":0.13301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24497,"mean_force":0.09071,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54774,0.0943,0.15144]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.0395,-0.00212],"force_p95":0.15785,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22245,"mean_force":0.132,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50067,0.03836,0.04023]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.5,0.01906,0.04175],"force_p95":0.0806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15073,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4995,0.03826,0.03895]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50289,0.01676,0.25193]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5064,0.03668,0.12526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.50001,0.05741,0.04077],"force_p95":0.07337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07988,"mean_force":0.04453,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49951,0.03826,0.03895]}],"total_contact_groups":16},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60554,0.1663,0.026],"final_tcp_position":[0.61952,0.16846,0.05814],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.71564,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50772,0.03465,0.20398],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50761,0.03892,0.04797],"tcp_start":[0.50772,0.03465,0.20398],"tcp_to_object_dist_end":0.02251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51245,0.03847,0.02558],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21329,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1512,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10875.0,"raw_peak_contact_force":0.22245,"subtask_id":"grasp_1","tcp_end":[0.49947,0.03826,0.03891],"tcp_start":[0.50761,0.03892,0.04797],"tcp_to_object_dist_end":0.01861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50882,0.03816,0.1142],"object_pos_start":[0.51245,0.03847,0.02558],"object_to_goal_dist_end":0.18194,"object_to_goal_dist_start":0.21329,"object_z_max":0.11409,"peak_contact_force":0.09849,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19447.0,"raw_peak_contact_force":0.50676,"tcp_end":[0.49546,0.03794,0.13461],"tcp_start":[0.49947,0.03826,0.03891],"tcp_to_object_dist_end":0.02439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60982,0.1542,0.11136],"object_pos_start":[0.50882,0.03816,0.1142],"object_to_goal_dist_end":0.04224,"object_to_goal_dist_start":0.18194,"object_z_max":0.12921,"peak_contact_force":0.13094,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21752.0,"raw_peak_contact_force":0.24684,"subtask_id":"transport_arc","tcp_end":[0.60592,0.15359,0.1468],"tcp_start":[0.49546,0.03794,0.13461],"tcp_to_object_dist_end":0.03566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.62205,0.16741,0.02058],"object_pos_start":[0.60982,0.1542,0.11136],"object_to_goal_dist_end":0.12468,"object_to_goal_dist_start":0.04224,"object_z_max":0.11136,"peak_contact_force":0.63182,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4825.0,"raw_peak_contact_force":0.63182,"tcp_end":[0.61952,0.16846,0.05814],"tcp_start":[0.60592,0.15359,0.1468],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60554,0.1663,0.026],"object_pos_start":[0.62205,0.16741,0.02058],"object_to_goal_dist_end":0.1212,"object_to_goal_dist_start":0.12468,"object_z_max":0.02626,"peak_contact_force":0.12501,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1701.0,"raw_peak_contact_force":0.71564,"subtask_id":"release_1","tcp_end":[0.61138,0.16615,0.07773],"tcp_start":[0.61952,0.16846,0.05814],"tcp_to_object_dist_end":0.05206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02439,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17949,"descend_1.grasp_z_offset":0.00296,"lift_1.lift_height":0.1084,"place_descend_1.place_height":0.07318,"transport_1.arc_height":0.37615,"transport_1.transport_speed":0.26481},"optimized_scores":{"best_composite_score":0.11466,"best_fitness_score":0.56466,"best_task_score":0.17067},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2355.0,"contact_point_centroid":[0.50465,0.09332,-0.00239],"force_p95":0.15174,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71714,"mean_force":0.14256,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52797,0.14782,0.21397]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.47966,0.04576,-0.00122],"force_p95":0.47197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64632,"mean_force":0.0862,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46895,0.04686,0.03171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9968.0,"contact_point_centroid":[0.46866,0.06559,0.07319],"force_p95":0.10414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31717,"mean_force":0.0628,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46651,0.04663,0.0715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3318.0,"contact_point_centroid":[0.47947,0.08085,0.14861],"force_p95":0.15757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31004,"mean_force":0.09605,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47387,0.06257,0.14925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2955.0,"contact_point_centroid":[0.47894,0.04348,0.14816],"force_p95":0.17821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29529,"mean_force":0.10421,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4735,0.0619,0.14841]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9616.0,"contact_point_centroid":[0.46865,0.02772,0.0753],"force_p95":0.10418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2942,"mean_force":0.06413,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4665,0.04663,0.07333]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04846,-0.00215],"force_p95":0.16653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24812,"mean_force":0.13443,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47155,0.04713,0.03094]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49052,0.02008,0.25839]},{"body_a":"world","body_b":"grasp_target","contact_count":2256.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47891,0.04474,0.12618]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.50464,0.09331,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.56741,0.21121,0.19206]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50464,0.09331,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57056,0.22101,0.16154]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5013.0,"contact_point_centroid":[0.47021,0.02778,0.03263],"force_p95":0.07014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11881,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47043,0.04702,0.02981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5530.0,"contact_point_centroid":[0.47002,0.06636,0.03201],"force_p95":0.07036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08049,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47044,0.04702,0.02982]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2267.0,"contact_point_centroid":[0.53193,0.15336,0.21875],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01564,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53151,0.15334,0.21649]},{"body_a":"left_finger","body_b":"right_finger","contact_count":972.0,"contact_point_centroid":[0.56789,0.21122,0.19432],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01054,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5674,0.21119,0.19213]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57372,0.22223,0.15965],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5732,0.22219,0.15749]}],"total_contact_groups":16},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50464,0.09331,0.01602],"final_tcp_position":[0.57485,0.22267,0.1608],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.71714,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1172.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48198,0.0419,0.21648],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4783,0.04779,0.03784],"tcp_start":[0.48198,0.0419,0.21648],"tcp_to_object_dist_end":0.01264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04724,0.02547],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29132,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15938,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12343.0,"raw_peak_contact_force":0.24812,"subtask_id":"grasp_1","tcp_end":[0.4704,0.04702,0.02978],"tcp_start":[0.4783,0.04779,0.03784],"tcp_to_object_dist_end":0.01295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.48239,0.04679,0.11362],"object_pos_start":[0.48261,0.04724,0.02547],"object_to_goal_dist_end":0.23812,"object_to_goal_dist_start":0.29132,"object_z_max":0.11352,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19718.0,"raw_peak_contact_force":0.64632,"tcp_end":[0.46648,0.04664,0.12675],"tcp_start":[0.4704,0.04702,0.02978],"tcp_to_object_dist_end":0.02063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50464,0.09331,0.01602],"object_pos_start":[0.48239,0.04679,0.11362],"object_to_goal_dist_end":0.2652,"object_to_goal_dist_start":0.23812,"object_z_max":0.15342,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10895.0,"raw_peak_contact_force":1.71714,"subtask_id":"transport_arc","tcp_end":[0.56201,0.20088,0.22548],"tcp_start":[0.46648,0.04664,0.12675],"tcp_to_object_dist_end":0.24236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.50464,0.09331,0.01602],"object_pos_start":[0.50464,0.09331,0.01602],"object_to_goal_dist_end":0.2652,"object_to_goal_dist_start":0.2652,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57485,0.22267,0.1608],"tcp_start":[0.56201,0.20088,0.22548],"tcp_to_object_dist_end":0.20645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50464,0.09331,0.01602],"object_pos_start":[0.50464,0.09331,0.01602],"object_to_goal_dist_end":0.2652,"object_to_goal_dist_start":0.2652,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.56901,0.22031,0.18135],"tcp_start":[0.57485,0.22267,0.1608],"tcp_to_object_dist_end":0.21819,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```