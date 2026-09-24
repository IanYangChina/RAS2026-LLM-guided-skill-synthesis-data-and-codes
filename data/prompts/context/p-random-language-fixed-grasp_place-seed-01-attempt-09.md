## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2590 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1466 | 0.44 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1891 | 0.42 | ✅ accepted |

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

## Current Skill (Q=0.259) — your mutation base

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
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
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
    - 0.0
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
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.02
      default: 0.008
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
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
    lift_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
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
    transport_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
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
    place_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.02
      default: 0.008
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (scale)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (scale)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (scale)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (scale)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], offset_along_axis={axis=world_z, distance=0.0, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (scale)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.259
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2559 |
| descend_1 | 1.00 | 1.00 | 0.0134 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1111 |
| transport_1 | 1.00 | 1.00 | 0.2382 |
| descend_place | 1.00 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.048) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.000, 0.048)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.279 | 1.00 / 42.667 | 0.172 | 0.250 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.027)→(0.462, -0.001, 0.138) | (0.479, -0.001, 0.025)→(0.475, -0.001, 0.133) | 0.279→0.250 | 1.00 / 40.000 | 0.083 | 0.720 |
| transport_1 | approach | 1.00 / step_budget | (0.462, -0.001, 0.138)→(0.596, 0.191, 0.141) | (0.475, -0.001, 0.133)→(0.598, 0.192, 0.132) | 0.250→0.026 | 1.00 / 39.000 | 0.081 | 0.130 |
| descend_place | descend | 1.00 / step_budget | (0.596, 0.191, 0.141)→(0.604, 0.202, 0.158) | (0.598, 0.192, 0.132)→(0.604, 0.203, 0.145) | 0.026→0.009 | 1.00 / 38.000 | 0.080 | 0.241 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.247
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.749
- phase_breakdown.release_1_score: 0.864
- phase_breakdown.approach_1_score: 0.645
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.659
- phase_breakdown.descend_1_score: 0.741
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.259
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.255


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61905,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1469,"approach_1.approach_tolerance":0.0185,"descend_1.descend_speed":0.06812,"descend_1.descend_tolerance":0.0107,"descend_place.place_speed":0.04239,"descend_place.place_tolerance":0.00806,"descend_place.place_z_offset":0.01709,"lift_1.lift_height":0.1264,"lift_1.lift_speed":0.08239,"lift_1.lift_tolerance":0.01721,"transport_1.transport_speed":0.16787,"transport_1.transport_tolerance":0.01763},"optimized_scores":{"best_composite_score":0.25669,"best_fitness_score":0.97669,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.4983,0.04073,-0.0016],"force_p95":0.5796,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77212,"mean_force":0.13543,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48543,0.04162,0.02718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6975.0,"contact_point_centroid":[0.48374,0.06066,0.0839],"force_p95":0.10458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42925,"mean_force":0.06668,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48282,0.0414,0.08125]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8979.0,"contact_point_centroid":[0.48479,0.02273,0.08014],"force_p95":0.0905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31866,"mean_force":0.05017,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48283,0.0414,0.07856]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50143,0.04477,-0.00232],"force_p95":0.21197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29419,"mean_force":0.1464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48802,0.04186,0.02659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12811.0,"contact_point_centroid":[0.55207,0.25602,0.14974],"force_p95":0.09584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25552,"mean_force":0.06321,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55698,0.23773,0.14574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.48849,0.02295,0.02695],"force_p95":0.07011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19147,"mean_force":0.04158,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48678,0.04175,0.0253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17696.0,"contact_point_centroid":[0.56365,0.2203,0.14548],"force_p95":0.08253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17294,"mean_force":0.04746,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55712,0.23795,0.14615]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13290.0,"contact_point_centroid":[0.52369,0.1201,0.13516],"force_p95":0.09216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15777,"mean_force":0.05384,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51836,0.13788,0.13484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9393.0,"contact_point_centroid":[0.5176,0.15704,0.13743],"force_p95":0.11527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15543,"mean_force":0.073,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51842,0.13793,0.1349]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4975,0.02,0.17463]},{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49542,0.04154,0.041]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.48777,0.06131,0.0282],"force_p95":0.09579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11053,"mean_force":0.05889,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48679,0.04176,0.02532]}],"total_contact_groups":12},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56516,0.24611,0.13834],"final_tcp_position":[0.56021,0.24277,0.15519],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.77212,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4968,0.04087,0.04744],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":46.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":184.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49537,0.04244,0.03436],"tcp_start":[0.4968,0.04087,0.04744],"tcp_to_object_dist_end":0.0105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50141,0.04261,0.02491],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24439,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.20128,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10948.0,"raw_peak_contact_force":0.29419,"subtask_id":"grasp_1","tcp_end":[0.48675,0.04175,0.02527],"tcp_start":[0.49537,0.04244,0.03436],"tcp_to_object_dist_end":0.01468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":426.0,"n_steps_budget":810.0,"object_pos_end":[0.49755,0.04218,0.13075],"object_pos_start":[0.50141,0.04261,0.02491],"object_to_goal_dist_end":0.21403,"object_to_goal_dist_start":0.24439,"object_z_max":0.13054,"peak_contact_force":0.10271,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16051.0,"raw_peak_contact_force":0.77212,"tcp_end":[0.48286,0.04141,0.13513],"tcp_start":[0.48675,0.04175,0.02527],"tcp_to_object_dist_end":0.01535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.5657,0.23598,0.12744],"object_pos_start":[0.49755,0.04218,0.13075],"object_to_goal_dist_end":0.02131,"object_to_goal_dist_start":0.21403,"object_z_max":0.13093,"peak_contact_force":0.10097,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22683.0,"raw_peak_contact_force":0.15777,"subtask_id":"transport_arc","tcp_end":[0.55596,0.23184,0.13865],"tcp_start":[0.48286,0.04141,0.13513],"tcp_to_object_dist_end":0.01541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.56516,0.24611,0.13834],"object_pos_start":[0.5657,0.23598,0.12744],"object_to_goal_dist_end":0.00856,"object_to_goal_dist_start":0.02131,"object_z_max":0.13833,"peak_contact_force":0.09556,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30507.0,"raw_peak_contact_force":0.25552,"subtask_id":"release_1","tcp_end":[0.56021,0.24277,0.15519],"tcp_start":[0.55596,0.23184,0.13865],"tcp_to_object_dist_end":0.01788,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61017,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05097,"approach_1.approach_tolerance":0.01576,"descend_1.descend_speed":0.0615,"descend_1.descend_tolerance":0.01066,"descend_place.place_speed":0.05984,"descend_place.place_tolerance":0.00921,"descend_place.place_z_offset":0.02528,"lift_1.lift_height":0.13686,"lift_1.lift_speed":0.06537,"lift_1.lift_tolerance":0.01633,"transport_1.transport_speed":0.06921,"transport_1.transport_tolerance":0.02251},"optimized_scores":{"best_composite_score":0.25945,"best_fitness_score":0.97945,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.47284,-0.01839,-0.00133],"force_p95":0.61307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7139,"mean_force":0.13932,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46209,-0.019,0.02861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8671.0,"contact_point_centroid":[0.45881,-0.03814,0.0899],"force_p95":0.07848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32357,"mean_force":0.05759,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45943,-0.01895,0.08724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10369.0,"contact_point_centroid":[0.4605,5e-05,0.08926],"force_p95":0.07394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31731,"mean_force":0.04951,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45943,-0.01895,0.0875]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18100.0,"contact_point_centroid":[0.61711,0.17121,0.19432],"force_p95":0.06934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2325,"mean_force":0.04741,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62132,0.15271,0.19128]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4762,-0.02007,-0.0021],"force_p95":0.1526,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21688,"mean_force":0.13027,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46451,-0.01904,0.02825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18100.0,"contact_point_centroid":[0.62523,0.13388,0.19201],"force_p95":0.07002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1859,"mean_force":0.04858,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62132,0.15271,0.19128]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48601,-0.00911,0.17325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.46447,5e-05,0.0286],"force_p95":0.06558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13097,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4633,-0.01902,0.02707]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47219,-0.01881,0.04066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11641.0,"contact_point_centroid":[0.54238,0.04806,0.1639],"force_p95":0.08017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12006,"mean_force":0.05308,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53987,0.06706,0.16237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11632.0,"contact_point_centroid":[0.5379,0.08527,0.16479],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1143,"mean_force":0.05241,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53923,0.06636,0.16226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4466.0,"contact_point_centroid":[0.46287,-0.0383,0.02981],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0847,"mean_force":0.04914,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4633,-0.01902,0.02707]}],"total_contact_groups":12},"final_pose_error":0.01091,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62867,0.15876,0.19316],"final_tcp_position":[0.62729,0.15777,0.2053],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.7139,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47363,-0.01857,0.04535],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":37.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":148.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4717,-0.01912,0.03539],"tcp_start":[0.47363,-0.01857,0.04535],"tcp_to_object_dist_end":0.01043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01939,0.02566],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28817,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15083,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11298.0,"raw_peak_contact_force":0.21688,"subtask_id":"grasp_1","tcp_end":[0.46327,-0.01901,0.02704],"tcp_start":[0.4717,-0.01912,0.03539],"tcp_to_object_dist_end":0.01287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":485.0,"n_steps_budget":870.0,"object_pos_end":[0.47188,-0.01941,0.14283],"object_pos_start":[0.47606,-0.01939,0.02566],"object_to_goal_dist_end":0.24409,"object_to_goal_dist_start":0.28817,"object_z_max":0.14262,"peak_contact_force":0.06904,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19127.0,"raw_peak_contact_force":0.7139,"tcp_end":[0.45955,-0.01894,0.14807],"tcp_start":[0.46327,-0.01901,0.02704],"tcp_to_object_dist_end":0.01341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.61795,0.1472,0.17019],"object_pos_start":[0.47188,-0.01941,0.14283],"object_to_goal_dist_end":0.0268,"object_to_goal_dist_start":0.24409,"object_z_max":0.17015,"peak_contact_force":0.0699,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23273.0,"raw_peak_contact_force":0.12006,"subtask_id":"transport_arc","tcp_end":[0.61655,0.14645,0.17904],"tcp_start":[0.45955,-0.01894,0.14807],"tcp_to_object_dist_end":0.009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.62867,0.15876,0.19316],"object_pos_start":[0.61795,0.1472,0.17019],"object_to_goal_dist_end":0.0042,"object_to_goal_dist_start":0.0268,"object_z_max":0.19315,"peak_contact_force":0.07049,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36200.0,"raw_peak_contact_force":0.2325,"subtask_id":"release_1","tcp_end":[0.62729,0.15777,0.2053],"tcp_start":[0.61655,0.14645,0.17904],"tcp_to_object_dist_end":0.01225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61749,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11574,"approach_1.approach_tolerance":0.02247,"descend_1.descend_speed":0.09987,"descend_1.descend_tolerance":0.01048,"descend_place.place_speed":0.08402,"descend_place.place_tolerance":0.0136,"descend_place.place_z_offset":0.01123,"lift_1.lift_height":0.11985,"lift_1.lift_speed":0.0256,"lift_1.lift_tolerance":0.01806,"transport_1.transport_speed":0.18879,"transport_1.transport_tolerance":0.02084},"optimized_scores":{"best_composite_score":0.26075,"best_fitness_score":0.98075,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45542,-0.02404,-0.00145],"force_p95":0.61541,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67263,"mean_force":0.15061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44552,-0.02466,0.02917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6354.0,"contact_point_centroid":[0.44212,-0.04379,0.08078],"force_p95":0.07994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30257,"mean_force":0.05756,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44303,-0.02459,0.07807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7759.0,"contact_point_centroid":[0.44389,-0.00556,0.07947],"force_p95":0.07473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29036,"mean_force":0.04837,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44303,-0.02459,0.07803]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45864,-0.02621,-0.00215],"force_p95":0.16627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23962,"mean_force":0.13402,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44789,-0.02473,0.02877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3880.0,"contact_point_centroid":[0.6145,0.21861,0.11296],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23427,"mean_force":0.04786,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6195,0.20044,0.10919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3880.0,"contact_point_centroid":[0.62439,0.18182,0.1092],"force_p95":0.07262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19079,"mean_force":0.04946,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6195,0.20044,0.10919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5246.0,"contact_point_centroid":[0.44754,-0.00562,0.02902],"force_p95":0.06611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15002,"mean_force":0.04128,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44671,-0.0247,0.02766]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47901,-0.01154,0.17715]},{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45607,-0.0242,0.04356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14677.0,"contact_point_centroid":[0.53526,0.07191,0.1172],"force_p95":0.07735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11233,"mean_force":0.053,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53272,0.0909,0.11597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15778.0,"contact_point_centroid":[0.52614,0.10411,0.11917],"force_p95":0.07076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10895,"mean_force":0.04872,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52828,0.08534,0.1165]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4504.0,"contact_point_centroid":[0.44598,-0.04401,0.0304],"force_p95":0.07929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08534,"mean_force":0.04916,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44672,-0.0247,0.02767]}],"total_contact_groups":12},"final_pose_error":0.01355,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61926,0.20451,0.10439],"final_tcp_position":[0.62363,0.20483,0.11396],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.67263,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45862,-0.02363,0.05178],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":220.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45496,-0.02488,0.0355],"tcp_start":[0.45862,-0.02363,0.05178],"tcp_to_object_dist_end":0.01024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02517,0.02548],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30296,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16297,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11550.0,"raw_peak_contact_force":0.23962,"subtask_id":"grasp_1","tcp_end":[0.44668,-0.02469,0.02764],"tcp_start":[0.45496,-0.02488,0.0355],"tcp_to_object_dist_end":0.01202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":353.0,"n_steps_budget":750.0,"object_pos_end":[0.45468,-0.02526,0.12555],"object_pos_start":[0.4585,-0.02517,0.02548],"object_to_goal_dist_end":0.29227,"object_to_goal_dist_start":0.30296,"object_z_max":0.12531,"peak_contact_force":0.07726,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14193.0,"raw_peak_contact_force":0.67263,"tcp_end":[0.44295,-0.02458,0.13],"tcp_start":[0.44668,-0.02469,0.02764],"tcp_to_object_dist_end":0.01256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.61066,0.19407,0.09777],"object_pos_start":[0.45468,-0.02526,0.12555],"object_to_goal_dist_end":0.0291,"object_to_goal_dist_start":0.29227,"object_z_max":0.12577,"peak_contact_force":0.07317,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30455.0,"raw_peak_contact_force":0.11233,"subtask_id":"transport_arc","tcp_end":[0.61615,0.19477,0.10653],"tcp_start":[0.44295,-0.02458,0.13],"tcp_to_object_dist_end":0.01037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.61926,0.20451,0.10439],"object_pos_start":[0.61066,0.19407,0.09777],"object_to_goal_dist_end":0.01505,"object_to_goal_dist_start":0.0291,"object_z_max":0.10435,"peak_contact_force":0.07259,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7760.0,"raw_peak_contact_force":0.23427,"subtask_id":"release_1","tcp_end":[0.62363,0.20483,0.11396],"tcp_start":[0.61615,0.19477,0.10653],"tcp_to_object_dist_end":0.01053,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```