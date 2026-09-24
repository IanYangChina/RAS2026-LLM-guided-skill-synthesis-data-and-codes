## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.3418 | 0.22 | ❌ rejected |
| 12 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.1639 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5857 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5858 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.5678 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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

## Current Skill (Q=-0.342) — your mutation base

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
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
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
    - 0.02
    tolerance: 0.005
  parameters:
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
  parameters:
    grasp_timeout:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: transport_arc
- id: place_1
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
    - 0.03
    tolerance: 0.01
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.342
- **task_score** (E): 0.220
- **fitness_score**: 0.178  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1569 |
| descend_1 | 0.00 | 1.00 | 0.0294 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_vertical_1 | 0.00 | 1.00 | 0.0936 |
| transport_1 | 0.33 | 1.00 | 0.1120 |
| place_1 | 0.00 | 1.00 | 0.0248 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.414, 0.001, 0.170) | (0.526, 0.005, 0.030)→(0.488, 0.010, 0.016) | 0.246→0.266 | 1.00 / 5.000 | 191.117 | 1373.921 |
| descend_1 | descend | 0.00 / step_budget | (0.414, 0.001, 0.170)→(0.413, 0.003, 0.196) | (0.488, 0.010, 0.016)→(0.488, 0.011, 0.016) | 0.266→0.267 | 1.00 / 5.000 | 255.962 | 415.612 |
| grasp_1 | grasp | 1.00 / step_budget | (0.413, 0.003, 0.195)→(0.413, 0.003, 0.195) | (0.488, 0.011, 0.016)→(0.488, 0.011, 0.016) | 0.267→0.267 | 1.00 / 9.000 | 72.501 | 102.839 |
| lift_vertical_1 | lift | 0.00 / step_budget | (0.441, 0.010, 0.191)→(0.495, 0.005, 0.267) | (0.488, 0.011, 0.016)→(0.488, 0.011, 0.016) | 0.267→0.267 | 1.00 / 10.000 | 267.925 | 820.984 |
| transport_1 | approach | 0.33 / step_budget | (0.495, 0.005, 0.267)→(0.546, 0.096, 0.293) | (0.489, 0.022, 0.016)→(0.487, 0.062, 0.015) | 0.260→0.243 | 1.00 / 9.333 | 273.353 | 468.389 |
| place_1 | descend | 0.00 / step_budget | (0.546, 0.096, 0.293)→(0.553, 0.103, 0.284) | (0.487, 0.062, 0.015)→(0.484, 0.060, 0.016) | 0.243→0.245 | 1.00 / 9.000 | 421.160 | 568.903 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.334
- phase_score: 0.169
- phase_breakdown.release_1_score: 0.024
- phase_breakdown.descend_1_score: 0.022
- phase_breakdown.transport_arc_score: 0.022
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.026
- grasp_place_fitness: 0.233

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.233
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.334
- **Median Q (composite search score)**: -0.347
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.385


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.96951,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07345,"descend_1.speed":0.07404,"grasp_1.grasp_timeout":1.88364,"lift_vertical_1.lift_height":0.12063,"lift_vertical_1.speed":0.06497,"place_1.place_z_offset":0.04234,"place_1.speed":0.06394,"transport_1.transport_speed":0.11001},"optimized_scores":{"best_composite_score":-0.34683,"best_fitness_score":0.17317,"best_task_score":0.22825},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63501,0.00018,-0.00046],"force_p95":201.35744,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1394.18081,"mean_force":199.12326,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40556,6e-05,0.1416]},{"body_a":"world","body_b":"link6","contact_count":1420.0,"contact_point_centroid":[0.6055,-0.02023,-0.00023],"force_p95":519.29919,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1278.14625,"mean_force":340.66247,"phase_index":3.0,"phase_name":"lift_vertical_1","phase_type":"lift","tcp_position_centroid":[0.47326,0.00064,0.23536]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.60782,-0.0001,-0.00024],"force_p95":404.72108,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":810.45808,"mean_force":233.17399,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.41323,0.00064,0.19356]},{"body_a":"world","body_b":"link6","contact_count":904.0,"contact_point_centroid":[0.63775,0.14293,-0.00032],"force_p95":443.70875,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.37376,"mean_force":346.18655,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.64611,0.14904,0.29357]},{"body_a":"world","body_b":"link6","contact_count":25.0,"contact_point_centroid":[0.57761,-0.04432,-7e-05],"force_p95":291.27419,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.26342,"mean_force":231.95884,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54967,-0.01322,0.29069]},{"body_a":"link5","body_b":"hand","contact_count":398.0,"contact_point_centroid":[0.51291,-0.12153,0.24401],"force_p95":192.49971,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.10724,"mean_force":152.63102,"phase_index":3.0,"phase_name":"lift_vertical_1","phase_type":"lift","tcp_position_centroid":[0.53516,-0.01924,0.2856]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61344,0.00801,-0.00014],"force_p95":80.94703,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.67081,"mean_force":75.2306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44484,0.0013,0.22349]},{"body_a":"grasp_target","body_b":"link6","contact_count":423.0,"contact_point_centroid":[0.54013,0.00087,0.02804],"force_p95":0.79886,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.67064,"mean_force":0.23957,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3946,-1e-05,0.11583]},{"body_a":"grasp_target","body_b":"link7","contact_count":350.0,"contact_point_centroid":[0.52568,0.00392,0.03101],"force_p95":1.57606,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.21049,"mean_force":0.38752,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3932,-3e-05,0.10842]},{"body_a":"grasp_target","body_b":"hand","contact_count":73.0,"contact_point_centroid":[0.5018,0.01143,0.04319],"force_p95":1.93028,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.98868,"mean_force":0.98068,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38545,-0.00012,0.06939]},{"body_a":"world","body_b":"grasp_target","contact_count":3813.0,"contact_point_centroid":[0.51343,0.00436,-0.00253],"force_p95":0.37586,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.66349,"mean_force":0.16765,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41723,9e-05,0.15115]},{"body_a":"grasp_target","body_b":"link6","contact_count":32.0,"contact_point_centroid":[0.53722,-0.00555,0.03746],"force_p95":1.03403,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.29637,"mean_force":0.64014,"phase_index":3.0,"phase_name":"lift_vertical_1","phase_type":"lift","tcp_position_centroid":[0.4067,0.04486,0.15672]},{"body_a":"grasp_target","body_b":"link6","contact_count":197.0,"contact_point_centroid":[0.54442,0.05262,0.031],"force_p95":0.63428,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.83553,"mean_force":0.39875,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58739,0.05475,0.30347]},{"body_a":"world","body_b":"grasp_target","contact_count":5782.0,"contact_point_centroid":[0.50829,0.01786,-0.00204],"force_p95":0.12704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73541,"mean_force":0.1284,"phase_index":3.0,"phase_name":"lift_vertical_1","phase_type":"lift","tcp_position_centroid":[0.47318,-0.00075,0.2346]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.51535,0.06727,-0.00329],"force_p95":0.57133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70277,"mean_force":0.23347,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58515,0.04977,0.30372]},{"body_a":"grasp_target","body_b":"link6","contact_count":188.0,"contact_point_centroid":[0.55214,0.1077,0.03367],"force_p95":0.20343,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56102,"mean_force":0.11001,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.64102,0.14415,0.29344]}],"total_contact_groups":26},"final_pose_error":0.06064,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.52088,0.10923,0.01602],"final_tcp_position":[0.65184,0.15462,0.29384],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1394.18081,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50832,0.00483,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.2712,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":191.14574,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5566.0,"raw_peak_contact_force":1394.18081,"subtask_id":"approach_1","tcp_end":[0.42828,0.00022,0.18801],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18976,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,0.00492,0.01602],"object_pos_start":[0.50832,0.00483,0.01602],"object_to_goal_dist_end":0.27195,"object_to_goal_dist_start":0.2712,"object_z_max":0.01607,"peak_contact_force":375.41087,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5304.0,"raw_peak_contact_force":810.45808,"subtask_id":"descend_1","tcp_end":[0.44494,0.00132,0.22426],"tcp_start":[0.42828,0.00022,0.18801],"tcp_to_object_dist_end":0.21725,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50674,0.00492,0.01602],"object_pos_start":[0.50674,0.00492,0.01602],"object_to_goal_dist_end":0.27195,"object_to_goal_dist_start":0.27195,"object_z_max":0.01602,"peak_contact_force":73.3899,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3505.0,"raw_peak_contact_force":137.67081,"subtask_id":"grasp_1","tcp_end":[0.44486,0.00129,0.22342],"tcp_start":[0.44486,0.00129,0.22342],"tcp_to_object_dist_end":0.21647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1474.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,0.00492,0.01602],"object_pos_start":[0.50674,0.00492,0.01602],"object_to_goal_dist_end":0.27195,"object_to_goal_dist_start":0.27195,"object_z_max":0.01924,"peak_contact_force":347.4714,"phase_name":"lift_vertical_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14013.0,"raw_peak_contact_force":1278.14625,"tcp_end":[0.54213,-0.01886,0.28537],"tcp_start":[0.46478,-0.01817,0.16844],"tcp_to_object_dist_end":0.27271,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.52018,0.11053,0.01543],"object_pos_start":[0.51108,0.0403,0.01602],"object_to_goal_dist_end":0.22218,"object_to_goal_dist_start":0.25134,"object_z_max":0.0182,"peak_contact_force":0.17337,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2676.0,"raw_peak_contact_force":292.26342,"subtask_id":"transport_arc","tcp_end":[0.63486,0.1358,0.32588],"tcp_start":[0.54213,-0.01886,0.28537],"tcp_to_object_dist_end":0.33191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52088,0.10923,0.01602],"object_pos_start":[0.52018,0.11053,0.01543],"object_to_goal_dist_end":0.2216,"object_to_goal_dist_start":0.22218,"object_z_max":0.01605,"peak_contact_force":434.42872,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9406.0,"raw_peak_contact_force":595.37376,"subtask_id":"release_1","tcp_end":[0.65184,0.15462,0.29384],"tcp_start":[0.63486,0.1358,0.32588],"tcp_to_object_dist_end":0.31048,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.68116,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05527,"descend_1.speed":0.01347,"grasp_1.grasp_timeout":0.97864,"lift_vertical_1.lift_height":0.13281,"lift_vertical_1.speed":0.07012,"place_1.place_z_offset":0.03391,"place_1.speed":0.07331,"transport_1.transport_speed":0.11068},"optimized_scores":{"best_composite_score":-0.28698,"best_fitness_score":0.23302,"best_task_score":0.33445},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63427,0.00387,-0.00046],"force_p95":199.11281,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1393.25885,"mean_force":200.00403,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39831,0.00365,0.132]},{"body_a":"world","body_b":"link6","contact_count":1458.0,"contact_point_centroid":[0.60966,0.03671,-0.0002],"force_p95":497.49483,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":884.3393,"mean_force":321.59077,"phase_index":3.0,"phase_name":"lift_vertical_1","phase_type":"lift","tcp_position_centroid":[0.43077,0.06664,0.20937]},{"body_a":"world","body_b":"link6","contact_count":961.0,"contact_point_centroid":[0.56435,0.07599,-0.0002],"force_p95":415.48266,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":522.75952,"mean_force":345.13268,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56806,0.09443,0.29312]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.59347,0.13256,-0.00032],"force_p95":436.34957,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":518.13317,"mean_force":346.9806,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59879,0.14202,0.29355]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.52699,-0.02032,0.24827],"force_p95":427.69392,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.82712,"mean_force":360.54051,"phase_index":3.0,"phase_name":"lift_vertical_1","phase_type":"lift","tcp_position_centroid":[0.50034,0.08732,0.25306]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61054,0.00965,-0.00025],"force_p95":199.73216,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.51623,"mean_force":195.86877,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38771,0.00969,0.15614]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.59856,0.01345,-0.00014],"force_p95":82.5719,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.15157,"mean_force":75.19627,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40021,0.01312,0.18746]},{"body_a":"grasp_target","body_b":"link7","contact_count":236.0,"contact_point_centroid":[0.5062,0.01854,0.03519],"force_p95":3.19687,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.56087,"mean_force":0.4653,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38866,0.00202,0.09809]},{"body_a":"grasp_target","body_b":"hand","contact_count":128.0,"contact_point_centroid":[0.49516,0.03904,0.05386],"force_p95":2.1129,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.76669,"mean_force":0.84661,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38538,0.00178,0.08375]},{"body_a":"world","body_b":"grasp_target","contact_count":3617.0,"contact_point_centroid":[0.50328,0.04534,-0.00226],"force_p95":0.37946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21953,"mean_force":0.15912,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41174,0.00356,0.14427]},{"body_a":"grasp_target","body_b":"link6","contact_count":680.0,"contact_point_centroid":[0.52212,0.08517,0.0336],"force_p95":0.22823,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.53417,"mean_force":0.13343,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5973,0.13878,0.29353]},{"body_a":"grasp_target","body_b":"link6","contact_count":951.0,"contact_point_centroid":[0.51231,0.06099,0.03711],"force_p95":0.56617,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.1191,"mean_force":0.36504,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56895,0.09548,0.2934]},{"body_a":"grasp_target","body_b":"link6","contact_count":115.0,"contact_point_centroid":[0.53767,0.03466,0.0307],"force_p95":0.88316,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.94375,"mean_force":0.44513,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38319,0.00179,0.08783]},{"body_a":"world","body_b":"grasp_target","contact_count":3240.0,"contact_point_centroid":[0.49119,0.07668,-0.00352],"force_p95":0.59739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6448,"mean_force":0.24194,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56853,0.09612,0.29281]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49256,0.09546,-0.00227],"force_p95":0.21789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60474,"mean_force":0.14115,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59878,0.14202,0.29355]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49765,0.04882,-0.00201],"force_p95":0.13705,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15153,"mean_force":0.12426,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38771,0.00969,0.15614]}],"total_contact_groups":25},"final_pose_error":0.15385,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49318,0.09628,0.01602],"final_tcp_position":[0.60395,0.15169,0.29346],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273060.86688,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49816,0.04852,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18994,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":191.7945,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5003.0,"raw_peak_contact_force":1393.25885,"subtask_id":"approach_1","tcp_end":[0.41268,0.00648,0.16806],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17942,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49751,0.04889,0.01602],"object_pos_start":[0.49816,0.04852,0.01602],"object_to_goal_dist_end":0.19004,"object_to_goal_dist_start":0.18994,"object_z_max":0.01603,"peak_contact_force":197.91645,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5243.0,"raw_peak_contact_force":226.51623,"subtask_id":"descend_1","tcp_end":[0.39988,0.01314,0.18758],"tcp_start":[0.41268,0.00648,0.16806],"tcp_to_object_dist_end":0.2006,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49751,0.04889,0.01602],"object_pos_start":[0.49751,0.04889,0.01602],"object_to_goal_dist_end":0.19004,"object_to_goal_dist_start":0.19004,"object_z_max":0.01602,"peak_contact_force":72.60688,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3504.0,"raw_peak_contact_force":85.15157,"subtask_id":"grasp_1","tcp_end":[0.40026,0.0131,0.18737],"tcp_start":[0.40026,0.0131,0.18738],"tcp_to_object_dist_end":0.20025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1508.0,"n_steps_budget":990.0,"object_pos_end":[0.4975,0.0489,0.01602],"object_pos_start":[0.49751,0.04889,0.01602],"object_to_goal_dist_end":0.19004,"object_to_goal_dist_start":0.19004,"object_z_max":0.01603,"peak_contact_force":231.74516,"phase_name":"lift_vertical_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13867.0,"raw_peak_contact_force":884.3393,"tcp_end":[0.52351,0.05721,0.2736],"tcp_start":[0.45532,0.06681,0.20148],"tcp_to_object_dist_end":0.25903,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49398,0.09593,0.0144],"object_pos_start":[0.4975,0.0489,0.01602],"object_to_goal_dist_end":0.16485,"object_to_goal_dist_start":0.19004,"object_z_max":0.01623,"peak_contact_force":353.57869,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9465.0,"raw_peak_contact_force":522.75952,"subtask_id":"transport_arc","tcp_end":[0.59241,0.13661,0.29348],"tcp_start":[0.52351,0.05721,0.2736],"tcp_to_object_dist_end":0.29871,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49318,0.09628,0.01602],"object_pos_start":[0.49398,0.09593,0.0144],"object_to_goal_dist_end":0.16429,"object_to_goal_dist_start":0.16485,"object_z_max":0.01603,"peak_contact_force":355.9204,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9917.0,"raw_peak_contact_force":518.13317,"subtask_id":"release_1","tcp_end":[0.60395,0.15169,0.29346],"tcp_start":[0.59241,0.13661,0.29348],"tcp_to_object_dist_end":0.30383,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.66929,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04463,"descend_1.speed":0.02101,"grasp_1.grasp_timeout":1.52178,"lift_vertical_1.lift_height":0.17574,"lift_vertical_1.speed":0.14553,"place_1.place_z_offset":0.02147,"place_1.speed":0.06117,"transport_1.transport_speed":0.12288},"optimized_scores":{"best_composite_score":-0.39161,"best_fitness_score":0.12839,"best_task_score":0.09824},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.6326,-0.00181,-0.00047],"force_p95":197.04885,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1334.32442,"mean_force":199.21053,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39203,-0.00186,0.12448]},{"body_a":"world","body_b":"link6","contact_count":981.0,"contact_point_centroid":[0.48276,0.04027,-0.00033],"force_p95":527.32534,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":593.20088,"mean_force":399.67834,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.39223,0.00191,0.26886]},{"body_a":"world","body_b":"link6","contact_count":978.0,"contact_point_centroid":[0.51232,0.01847,-0.00031],"force_p95":520.38348,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":590.14452,"mean_force":387.98608,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.3993,0.0024,0.26241]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.5293,0.00329,-0.00299],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":415.79266,"mean_force":19.79965,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3737,-0.00119,0.0511]},{"body_a":"world","body_b":"link6","contact_count":819.0,"contact_point_centroid":[0.58322,-0.01087,-0.00022],"force_p95":224.7481,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.46686,"mean_force":208.03339,"phase_index":3.0,"phase_name":"lift_vertical_1","phase_type":"lift","tcp_position_centroid":[0.38716,-0.01749,0.19278]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61318,-0.00451,-0.00026],"force_p95":196.14028,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.86221,"mean_force":193.97745,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38434,-0.00487,0.14753]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60336,-0.00642,-0.00014],"force_p95":82.92424,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.69332,"mean_force":74.4598,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39405,-0.00655,0.17517]},{"body_a":"grasp_target","body_b":"link7","contact_count":413.0,"contact_point_centroid":[0.49121,-0.01824,0.03984],"force_p95":0.87621,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.35373,"mean_force":0.40947,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38745,-0.00132,0.10632]},{"body_a":"grasp_target","body_b":"hand","contact_count":386.0,"contact_point_centroid":[0.48485,-0.02863,0.05561],"force_p95":1.96806,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.16627,"mean_force":0.42815,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38735,-0.0013,0.10462]},{"body_a":"world","body_b":"grasp_target","contact_count":3073.0,"contact_point_centroid":[0.47366,-0.0197,-0.00314],"force_p95":0.41075,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29603,"mean_force":0.21489,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4082,-0.00181,0.13938]},{"body_a":"grasp_target","body_b":"link6","contact_count":583.0,"contact_point_centroid":[0.45646,0.00323,0.03501],"force_p95":0.4131,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.18735,"mean_force":0.25799,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.38816,0.00082,0.27046]},{"body_a":"grasp_target","body_b":"link6","contact_count":604.0,"contact_point_centroid":[0.4707,-0.00496,0.0337],"force_p95":0.43663,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.02648,"mean_force":0.28878,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.39518,-0.00066,0.26405]},{"body_a":"world","body_b":"grasp_target","contact_count":3896.0,"contact_point_centroid":[0.43941,-0.02387,-0.0023],"force_p95":0.2723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71351,"mean_force":0.15243,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.39249,0.00199,0.26875]},{"body_a":"world","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.44781,-0.02095,-0.00248],"force_p95":0.36444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59961,"mean_force":0.16416,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.39983,0.00242,0.26206]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02196,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38434,-0.00487,0.14753]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45856,-0.02196,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39405,-0.00655,0.17517]}],"total_contact_groups":21},"final_pose_error":0.26034,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.43878,-0.02546,0.01602],"final_tcp_position":[0.40212,0.00414,0.26482],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273004.12065,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02196,0.01602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.33793,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":190.41125,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4779.0,"raw_peak_contact_force":1334.32442,"subtask_id":"approach_1","tcp_end":[0.40071,-0.00303,0.15264],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14957,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02196,0.01602],"object_pos_start":[0.45856,-0.02196,0.01602],"object_to_goal_dist_end":0.33793,"object_to_goal_dist_start":0.33793,"object_z_max":0.01602,"peak_contact_force":194.55761,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":209.86221,"subtask_id":"descend_1","tcp_end":[0.39369,-0.0065,0.17535],"tcp_start":[0.40071,-0.00303,0.15264],"tcp_to_object_dist_end":0.17273,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02196,0.01602],"object_pos_start":[0.45856,-0.02196,0.01602],"object_to_goal_dist_end":0.33793,"object_to_goal_dist_start":0.33793,"object_z_max":0.01602,"peak_contact_force":71.5073,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3503.0,"raw_peak_contact_force":85.69332,"subtask_id":"grasp_1","tcp_end":[0.39412,-0.00658,0.17506],"tcp_start":[0.39412,-0.00658,0.17506],"tcp_to_object_dist_end":0.17229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":823.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02196,0.01602],"object_pos_start":[0.45856,-0.02196,0.01602],"object_to_goal_dist_end":0.33793,"object_to_goal_dist_start":0.33793,"object_z_max":0.01602,"peak_contact_force":224.55979,"phase_name":"lift_vertical_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7588.0,"raw_peak_contact_force":300.46686,"tcp_end":[0.41798,-0.02465,0.24077],"tcp_start":[0.40167,-0.01772,0.20403],"tcp_to_object_dist_end":0.2284,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44713,-0.0216,0.01602],"object_pos_start":[0.45856,-0.02196,0.01602],"object_to_goal_dist_end":0.34222,"object_to_goal_dist_start":0.33793,"object_z_max":0.01628,"peak_contact_force":466.30572,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9688.0,"raw_peak_contact_force":590.14452,"subtask_id":"transport_arc","tcp_end":[0.4101,0.01482,0.25927],"tcp_start":[0.41798,-0.02465,0.24077],"tcp_to_object_dist_end":0.24874,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43878,-0.02546,0.01602],"object_pos_start":[0.44713,-0.0216,0.01602],"object_to_goal_dist_end":0.34805,"object_to_goal_dist_start":0.34222,"object_z_max":0.01642,"peak_contact_force":473.13161,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9915.0,"raw_peak_contact_force":593.20088,"subtask_id":"release_1","tcp_end":[0.40212,0.00414,0.26482],"tcp_start":[0.4101,0.01482,0.25927],"tcp_to_object_dist_end":0.25322,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```