## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5091 | 1.00 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2592 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2924 | 0.57 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2590 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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

## Current Skill (Q=0.509) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
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
    tolerance: 0.08
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: scale
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
    - 0.0
    tolerance: 0.015
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: impedance_control
  termination: grasp_success
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
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: scale
- id: transport_1
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
    tolerance: 0.03
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: scale
  subtask_id: transport_arc
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
    offset_along_axis:
      distance: 0.0
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.025
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale
    place_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.08
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (scale)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (scale)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (scale)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (scale)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], offset_along_axis={axis=world_z, distance=0.0, mode=add_to_offset, sign=positive}, tolerance=0.025
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (scale)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.509
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1949 |
| descend_1 | 1.00 | 1.00 | 0.0695 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.0921 |
| transport_1 | 1.00 | 1.00 | 0.2282 |
| descend_place | 1.00 | 1.00 | 0.0160 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, -0.000, 0.108) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.488, -0.000, 0.108)→(0.476, -0.001, 0.040) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.476, -0.001, 0.040)→(0.467, -0.001, 0.031) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.279 | 1.00 / 42.333 | 0.186 | 0.265 |
| lift_1 | lift | 1.00 / step_budget | (0.467, -0.001, 0.031)→(0.464, -0.001, 0.123) | (0.479, -0.001, 0.025)→(0.476, -0.001, 0.117) | 0.279→0.252 | 1.00 / 39.333 | 0.083 | 0.650 |
| transport_1 | approach | 1.00 / step_budget | (0.464, -0.001, 0.123)→(0.592, 0.183, 0.140) | (0.476, -0.001, 0.117)→(0.600, 0.186, 0.131) | 0.252→0.029 | 1.00 / 37.667 | 0.086 | 0.139 |
| descend_place | descend | 1.00 / step_budget | (0.592, 0.183, 0.140)→(0.598, 0.193, 0.149) | (0.600, 0.186, 0.131)→(0.606, 0.197, 0.141) | 0.029→0.014 | 1.00 / 37.000 | 0.086 | 0.275 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.076
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.650
- phase_breakdown.release_1_score: 0.706
- phase_breakdown.approach_1_score: 0.207
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.549
- phase_breakdown.descend_1_score: 0.821
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.510
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 5.3
- **Final σ (mean)**: 0.338


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79762,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13774,"descend_1.descend_speed":0.05257,"descend_place.place_speed":0.05597,"descend_place.place_z_offset":0.02452,"lift_1.lift_height":0.12295,"lift_1.lift_speed":0.07919,"transport_1.transport_speed":0.18641},"optimized_scores":{"best_composite_score":0.50678,"best_fitness_score":0.97678,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.49804,0.04076,-0.00192],"force_p95":0.61162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70231,"mean_force":0.20298,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48642,0.04051,0.03164]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2987.0,"contact_point_centroid":[0.48496,0.0596,0.0767],"force_p95":0.09581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37185,"mean_force":0.0684,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48458,0.04034,0.0743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":786.0,"contact_point_centroid":[0.55098,0.24509,0.14678],"force_p95":0.11481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34716,"mean_force":0.08748,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55309,0.22609,0.1422]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3921.0,"contact_point_centroid":[0.4863,0.02144,0.07579],"force_p95":0.08857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31235,"mean_force":0.05338,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48458,0.04034,0.07436]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50145,0.04468,-0.00241],"force_p95":0.23345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30562,"mean_force":0.15227,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48907,0.04076,0.03134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.56067,0.20904,0.14186],"force_p95":0.1001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19369,"mean_force":0.05974,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55309,0.22612,0.14222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4908.0,"contact_point_centroid":[0.4896,0.02171,0.03148],"force_p95":0.08257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1678,"mean_force":0.04338,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48785,0.04065,0.03006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5515.0,"contact_point_centroid":[0.51563,0.14854,0.1325],"force_p95":0.10404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15598,"mean_force":0.06565,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51698,0.12956,0.1285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7133.0,"contact_point_centroid":[0.52163,0.11058,0.12923],"force_p95":0.08991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14901,"mean_force":0.05373,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51669,0.12869,0.12848]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.50118,0.04505,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1236,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50248,0.01399,0.21318]},{"body_a":"world","body_b":"grasp_target","contact_count":512.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49661,0.0363,0.06672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4219.0,"contact_point_centroid":[0.48822,0.06028,0.0326],"force_p95":0.09631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10232,"mean_force":0.05465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48786,0.04065,0.03008]}],"total_contact_groups":12},"final_pose_error":0.02486,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57135,0.23983,0.14216],"final_tcp_position":[0.55616,0.23338,0.15086],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.70231,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12258,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":500.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50345,0.03113,0.10814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08332,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":512.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49658,0.04129,0.0394],"tcp_start":[0.50345,0.03113,0.10814],"tcp_to_object_dist_end":0.01464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50135,0.0418,0.02461],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24523,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.22078,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10927.0,"raw_peak_contact_force":0.30562,"subtask_id":"grasp_1","tcp_end":[0.48782,0.04065,0.03003],"tcp_start":[0.49658,0.04129,0.0394],"tcp_to_object_dist_end":0.01463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":186.0,"n_steps_budget":780.0,"object_pos_end":[0.49834,0.0415,0.11733],"object_pos_start":[0.50135,0.0418,0.02461],"object_to_goal_dist_end":0.21585,"object_to_goal_dist_start":0.24523,"object_z_max":0.11684,"peak_contact_force":0.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6979.0,"raw_peak_contact_force":0.70231,"tcp_end":[0.48444,0.04033,0.12353],"tcp_start":[0.48782,0.04065,0.03003],"tcp_to_object_dist_end":0.01527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.56717,0.2258,0.12846],"object_pos_start":[0.49834,0.0415,0.11733],"object_to_goal_dist_end":0.02658,"object_to_goal_dist_start":0.21585,"object_z_max":0.12842,"peak_contact_force":0.11441,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12648.0,"raw_peak_contact_force":0.15598,"subtask_id":"transport_arc","tcp_end":[0.55174,0.2197,0.1367],"tcp_start":[0.48444,0.04033,0.12353],"tcp_to_object_dist_end":0.01853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":68.0,"n_steps_budget":1000.0,"object_pos_end":[0.57135,0.23983,0.14216],"object_pos_start":[0.56717,0.2258,0.12846],"object_to_goal_dist_end":0.00973,"object_to_goal_dist_start":0.02658,"object_z_max":0.14191,"peak_contact_force":0.11327,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2098.0,"raw_peak_contact_force":0.34716,"subtask_id":"release_1","tcp_end":[0.55616,0.23338,0.15086],"tcp_start":[0.55174,0.2197,0.1367],"tcp_to_object_dist_end":0.01866,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80571,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.12403,"descend_1.descend_speed":0.06321,"descend_place.place_speed":0.06888,"descend_place.place_z_offset":0.01516,"lift_1.lift_height":0.1265,"lift_1.lift_speed":0.11588,"transport_1.transport_speed":0.1966},"optimized_scores":{"best_composite_score":0.50955,"best_fitness_score":0.97955,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.47302,-0.01868,-0.00161],"force_p95":0.59262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65134,"mean_force":0.22182,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46374,-0.01847,0.03299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3402.0,"contact_point_centroid":[0.46062,-0.03766,0.08039],"force_p95":0.08132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32066,"mean_force":0.06069,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46184,-0.01844,0.07786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4158.0,"contact_point_centroid":[0.46227,0.0006,0.0792],"force_p95":0.07712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30604,"mean_force":0.0511,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46184,-0.01844,0.07786]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47623,-0.02007,-0.00215],"force_p95":0.16602,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23501,"mean_force":0.13405,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46617,-0.01851,0.03294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.61112,0.16407,0.18234],"force_p95":0.07546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23431,"mean_force":0.05238,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61511,0.14552,0.17933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.61891,0.12665,0.1801],"force_p95":0.07475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18702,"mean_force":0.05219,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61511,0.14552,0.17933]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5258.0,"contact_point_centroid":[0.46544,0.0006,0.03311],"force_p95":0.06766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14709,"mean_force":0.04124,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46498,-0.01849,0.03176]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.47616,-0.02015,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12362,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49462,-0.0062,0.21377]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8283.0,"contact_point_centroid":[0.5405,0.04545,0.15349],"force_p95":0.08164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13572,"mean_force":0.05479,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53886,0.06461,0.15168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9100.0,"contact_point_centroid":[0.53389,0.07996,0.15338],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1254,"mean_force":0.04942,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53556,0.0611,0.15062]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47637,-0.01633,0.06805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4512.0,"contact_point_centroid":[0.46385,-0.0378,0.03444],"force_p95":0.07857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08174,"mean_force":0.04899,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46498,-0.01849,0.03177]}],"total_contact_groups":12},"final_pose_error":0.02489,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62836,0.15249,0.17696],"final_tcp_position":[0.61965,0.15019,0.18517],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.65134,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12257,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":492.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48612,-0.01391,0.10913],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08393,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":500.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47355,-0.01856,0.04039],"tcp_start":[0.48612,-0.01391,0.10913],"tcp_to_object_dist_end":0.01469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01906,0.02546],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28806,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.16255,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11570.0,"raw_peak_contact_force":0.23501,"subtask_id":"grasp_1","tcp_end":[0.46495,-0.01849,0.03173],"tcp_start":[0.47355,-0.01856,0.04039],"tcp_to_object_dist_end":0.0128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":189.0,"n_steps_budget":810.0,"object_pos_end":[0.47324,-0.01908,0.12177],"object_pos_start":[0.4761,-0.01906,0.02546],"object_to_goal_dist_end":0.24791,"object_to_goal_dist_start":0.28806,"object_z_max":0.12126,"peak_contact_force":0.07808,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7624.0,"raw_peak_contact_force":0.65134,"tcp_end":[0.46172,-0.01843,0.12855],"tcp_start":[0.46495,-0.01849,0.03173],"tcp_to_object_dist_end":0.01338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.62051,0.14352,0.16772],"object_pos_start":[0.47324,-0.01908,0.12177],"object_to_goal_dist_end":0.02936,"object_to_goal_dist_start":0.24791,"object_z_max":0.16763,"peak_contact_force":0.07249,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17383.0,"raw_peak_contact_force":0.13572,"subtask_id":"transport_arc","tcp_end":[0.61224,0.14147,0.17609],"tcp_start":[0.46172,-0.01843,0.12855],"tcp_to_object_dist_end":0.01194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.62836,0.15249,0.17696],"object_pos_start":[0.62051,0.14352,0.16772],"object_to_goal_dist_end":0.01499,"object_to_goal_dist_start":0.02936,"object_z_max":0.17673,"peak_contact_force":0.07208,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.23431,"subtask_id":"release_1","tcp_end":[0.61965,0.15019,0.18517],"tcp_start":[0.61224,0.14147,0.17609],"tcp_to_object_dist_end":0.01219,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80874,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11267,"descend_1.descend_speed":0.06176,"descend_place.place_speed":0.06279,"descend_place.place_z_offset":0.01555,"lift_1.lift_height":0.11518,"lift_1.lift_speed":0.08075,"transport_1.transport_speed":0.17248},"optimized_scores":{"best_composite_score":0.51088,"best_fitness_score":0.98088,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.45565,-0.02403,-0.00169],"force_p95":0.54679,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59487,"mean_force":0.19812,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44767,-0.02405,0.03368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3415.0,"contact_point_centroid":[0.44718,-0.00495,0.07507],"force_p95":0.0811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29228,"mean_force":0.05404,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4459,-0.02401,0.07367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3051.0,"contact_point_centroid":[0.44457,-0.04313,0.0747],"force_p95":0.08256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29044,"mean_force":0.06,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44591,-0.02401,0.0724]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45865,-0.02616,-0.00222],"force_p95":0.18125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25362,"mean_force":0.13837,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45011,-0.02412,0.03341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.60811,0.20963,0.11139],"force_p95":0.07655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24394,"mean_force":0.05164,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61292,0.19139,0.10771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.61769,0.17273,0.10781],"force_p95":0.07574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19411,"mean_force":0.0521,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61292,0.19139,0.10771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4763.0,"contact_point_centroid":[0.45047,-0.00499,0.03379],"force_p95":0.07457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16658,"mean_force":0.04522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44895,-0.02409,0.0323]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.45856,-0.02632,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1236,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48895,-0.00823,0.21261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9934.0,"contact_point_centroid":[0.5289,0.06174,0.11178],"force_p95":0.0776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12498,"mean_force":0.05202,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52655,0.08079,0.11063]},{"body_a":"world","body_b":"grasp_target","contact_count":488.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46205,-0.02142,0.06731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10086.0,"contact_point_centroid":[0.52411,0.09916,0.11322],"force_p95":0.07419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11897,"mean_force":0.04972,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52619,0.08032,0.11065]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4554.0,"contact_point_centroid":[0.44737,-0.04336,0.03476],"force_p95":0.08253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08552,"mean_force":0.04901,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44896,-0.02409,0.03231]}],"total_contact_groups":12},"final_pose_error":0.02487,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61967,0.19814,0.1027],"final_tcp_position":[0.61721,0.19674,0.11178],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.59487,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12258,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":500.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47367,-0.0184,0.10684],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08259,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":122.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":488.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.45735,-0.02424,0.04044],"tcp_start":[0.47367,-0.0184,0.10684],"tcp_to_object_dist_end":0.01462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45855,-0.02474,0.02525],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30266,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.17461,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11117.0,"raw_peak_contact_force":0.25362,"subtask_id":"grasp_1","tcp_end":[0.44892,-0.02408,0.03228],"tcp_start":[0.45735,-0.02424,0.04044],"tcp_to_object_dist_end":0.01194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":167.0,"n_steps_budget":750.0,"object_pos_end":[0.45602,-0.02478,0.11059],"object_pos_start":[0.45855,-0.02474,0.02525],"object_to_goal_dist_end":0.29089,"object_to_goal_dist_start":0.30266,"object_z_max":0.11009,"peak_contact_force":0.07805,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6532.0,"raw_peak_contact_force":0.59487,"tcp_end":[0.44572,-0.024,0.11801],"tcp_start":[0.44892,-0.02408,0.03228],"tcp_to_object_dist_end":0.01271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.61268,0.18817,0.09699],"object_pos_start":[0.45602,-0.02478,0.11059],"object_to_goal_dist_end":0.03162,"object_to_goal_dist_start":0.29089,"object_z_max":0.11172,"peak_contact_force":0.07214,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20020.0,"raw_peak_contact_force":0.12498,"subtask_id":"transport_arc","tcp_end":[0.61055,0.18696,0.10624],"tcp_start":[0.44572,-0.024,0.11801],"tcp_to_object_dist_end":0.00957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":51.0,"n_steps_budget":1000.0,"object_pos_end":[0.61967,0.19814,0.1027],"object_pos_start":[0.61268,0.18817,0.09699],"object_to_goal_dist_end":0.01847,"object_to_goal_dist_start":0.03162,"object_z_max":0.10253,"peak_contact_force":0.07209,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.24394,"subtask_id":"release_1","tcp_end":[0.61721,0.19674,0.11178],"tcp_start":[0.61055,0.18696,0.10624],"tcp_to_object_dist_end":0.00951,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```