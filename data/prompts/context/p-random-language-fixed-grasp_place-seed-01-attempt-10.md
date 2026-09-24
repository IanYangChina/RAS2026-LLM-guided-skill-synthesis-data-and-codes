## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2590 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1466 | 0.44 | ✅ accepted |

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
| approach_1 | 1.00 | 1.00 | 0.2567 |
| descend_1 | 1.00 | 1.00 | 0.0130 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1080 |
| transport_1 | 0.67 | 1.00 | 0.2281 |
| descend_place | 1.00 | 1.00 | 0.0285 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, 0.000, 0.047) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, 0.000, 0.047)→(0.474, -0.000, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.035)→(0.466, -0.001, 0.026) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.278 | 1.00 / 42.667 | 0.170 | 0.248 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.026)→(0.462, -0.001, 0.134) | (0.479, -0.001, 0.025)→(0.475, -0.001, 0.128) | 0.278→0.252 | 1.00 / 37.333 | 0.092 | 0.717 |
| transport_1 | approach | 0.67 / step_budget | (0.462, -0.001, 0.134)→(0.589, 0.182, 0.142) | (0.475, -0.001, 0.128)→(0.591, 0.183, 0.132) | 0.252→0.037 | 1.00 / 36.667 | 55983.958 | 0.138 |
| descend_place | descend | 1.00 / step_budget | (0.589, 0.182, 0.142)→(0.602, 0.200, 0.156) | (0.591, 0.183, 0.132)→(0.603, 0.201, 0.144) | 0.037→0.011 | 1.00 / 37.333 | 0.080 | 0.286 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.024
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.555
- phase_breakdown.release_1_score: 0.774
- phase_breakdown.approach_1_score: 0.554
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.343
- phase_breakdown.descend_1_score: 0.729
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
- **Final σ (mean)**: 0.284


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55689,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11117,"approach_1.approach_tolerance":0.01098,"descend_1.descend_speed":0.06286,"descend_1.descend_tolerance":0.01013,"descend_place.place_speed":0.09668,"descend_place.place_tolerance":0.01205,"descend_place.place_z_offset":0.0243,"lift_1.lift_height":0.12169,"lift_1.lift_speed":0.0724,"lift_1.lift_tolerance":0.00754,"transport_1.transport_speed":0.18745,"transport_1.transport_tolerance":0.02083},"optimized_scores":{"best_composite_score":0.25678,"best_fitness_score":0.97678,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":232.0,"contact_point_centroid":[0.49694,0.04111,-0.00148],"force_p95":0.43254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80998,"mean_force":0.12065,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48466,0.0418,0.02681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4674.0,"contact_point_centroid":[0.55216,0.25425,0.15264],"force_p95":0.09751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44175,"mean_force":0.0713,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55633,0.23578,0.14892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12301.0,"contact_point_centroid":[0.48342,0.06087,0.0814],"force_p95":0.1054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42785,"mean_force":0.06275,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48256,0.04162,0.07879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14950.0,"contact_point_centroid":[0.48476,0.02301,0.07717],"force_p95":0.08987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31926,"mean_force":0.05023,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48256,0.04162,0.07573]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6989.0,"contact_point_centroid":[0.5633,0.21842,0.14768],"force_p95":0.08489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3093,"mean_force":0.05181,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55633,0.23579,0.14894]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50141,0.04478,-0.0023],"force_p95":0.20546,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28628,"mean_force":0.14469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48806,0.04211,0.02618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5159.0,"contact_point_centroid":[0.48843,0.02317,0.02657],"force_p95":0.06776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20191,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48682,0.042,0.02489]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6663.0,"contact_point_centroid":[0.51788,0.15631,0.13676],"force_p95":0.11738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17574,"mean_force":0.08069,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51812,0.13714,0.13463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9677.0,"contact_point_centroid":[0.52213,0.11496,0.13422],"force_p95":0.09697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16495,"mean_force":0.05863,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51633,0.13253,0.1345]},{"body_a":"world","body_b":"grasp_target","contact_count":3064.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49708,0.02091,0.16881]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49547,0.04237,0.03685]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.4877,0.06151,0.02781],"force_p95":0.09498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10947,"mean_force":0.05815,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48683,0.042,0.02491]}],"total_contact_groups":12},"final_pose_error":0.01199,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56742,0.2461,0.1446],"final_tcp_position":[0.55973,0.24183,0.16046],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3064.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49636,0.0422,0.03922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":100.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49538,0.0427,0.03391],"tcp_start":[0.49636,0.0422,0.03922],"tcp_to_object_dist_end":0.01007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50139,0.0428,0.02499],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2442,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19586,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11058.0,"raw_peak_contact_force":0.28628,"subtask_id":"grasp_1","tcp_end":[0.48679,0.04199,0.02486],"tcp_start":[0.49538,0.0427,0.03391],"tcp_to_object_dist_end":0.01462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.4966,0.04254,0.1262],"object_pos_start":[0.50139,0.0428,0.02499],"object_to_goal_dist_end":0.21438,"object_to_goal_dist_start":0.2442,"object_z_max":0.12609,"peak_contact_force":0.11862,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27483.0,"raw_peak_contact_force":0.80998,"tcp_end":[0.48278,0.04165,0.13472],"tcp_start":[0.48679,0.04199,0.02486],"tcp_to_object_dist_end":0.01626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.5651,0.23322,0.12517],"object_pos_start":[0.4966,0.04254,0.1262],"object_to_goal_dist_end":0.02455,"object_to_goal_dist_start":0.21438,"object_z_max":0.12623,"peak_contact_force":167951.73011,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16340.0,"raw_peak_contact_force":0.17574,"subtask_id":"transport_arc","tcp_end":[0.55467,0.22848,0.13845],"tcp_start":[0.48278,0.04165,0.13472],"tcp_to_object_dist_end":0.01754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.56742,0.2461,0.1446],"object_pos_start":[0.5651,0.23322,0.12517],"object_to_goal_dist_end":0.00391,"object_to_goal_dist_start":0.02455,"object_z_max":0.14455,"peak_contact_force":0.09601,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11663.0,"raw_peak_contact_force":0.44175,"subtask_id":"release_1","tcp_end":[0.55973,0.24183,0.16046],"tcp_start":[0.55467,0.22848,0.13845],"tcp_to_object_dist_end":0.01815,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57225,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1463,"approach_1.approach_tolerance":0.01395,"descend_1.descend_speed":0.07387,"descend_1.descend_tolerance":0.0107,"descend_place.place_speed":0.06424,"descend_place.place_tolerance":0.01237,"descend_place.place_z_offset":0.01331,"lift_1.lift_height":0.11384,"lift_1.lift_speed":0.06403,"lift_1.lift_tolerance":0.01402,"transport_1.transport_speed":0.21171,"transport_1.transport_tolerance":0.02027},"optimized_scores":{"best_composite_score":0.25942,"best_fitness_score":0.97942,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.47268,-0.01815,-0.00131],"force_p95":0.50607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66387,"mean_force":0.12041,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46206,-0.01901,0.02875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8766.0,"contact_point_centroid":[0.45888,-0.03816,0.08047],"force_p95":0.07884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2997,"mean_force":0.05775,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45932,-0.01895,0.07774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10675.0,"contact_point_centroid":[0.46043,5e-05,0.0796],"force_p95":0.07301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29627,"mean_force":0.04882,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45931,-0.01895,0.07768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5640.0,"contact_point_centroid":[0.61809,0.1721,0.18771],"force_p95":0.0695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23558,"mean_force":0.04799,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6223,0.1536,0.18464]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4762,-0.02008,-0.0021],"force_p95":0.15235,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21662,"mean_force":0.1302,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4645,-0.01905,0.02834]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5640.0,"contact_point_centroid":[0.62622,0.13477,0.18535],"force_p95":0.07023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18972,"mean_force":0.04899,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6223,0.1536,0.18464]},{"body_a":"world","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48581,-0.0092,0.17206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.46446,4e-05,0.02869],"force_p95":0.06557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13122,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46329,-0.01903,0.02716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13787.0,"contact_point_centroid":[0.54511,0.05111,0.15434],"force_p95":0.08049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13071,"mean_force":0.05398,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54241,0.07011,0.15275]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14251.0,"contact_point_centroid":[0.53897,0.08674,0.15452],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12535,"mean_force":0.05181,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54026,0.06786,0.15204]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4721,-0.01888,0.03987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4465.0,"contact_point_centroid":[0.46287,-0.03831,0.02991],"force_p95":0.07659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08463,"mean_force":0.04914,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4633,-0.01903,0.02716]}],"total_contact_groups":12},"final_pose_error":0.01233,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62861,0.15837,0.17997],"final_tcp_position":[0.62642,0.15718,0.19224],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.66387,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2500.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47338,-0.0187,0.04359],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":128.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47169,-0.01913,0.03548],"tcp_start":[0.47338,-0.0187,0.04359],"tcp_to_object_dist_end":0.01051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.0194,0.02566],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28818,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15061,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11297.0,"raw_peak_contact_force":0.21662,"subtask_id":"grasp_1","tcp_end":[0.46326,-0.01902,0.02713],"tcp_start":[0.47169,-0.01913,0.03548],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":494.0,"n_steps_budget":720.0,"object_pos_end":[0.47182,-0.01949,0.1208],"object_pos_start":[0.47606,-0.0194,0.02566],"object_to_goal_dist_end":0.24938,"object_to_goal_dist_start":0.28818,"object_z_max":0.12065,"peak_contact_force":0.07965,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19538.0,"raw_peak_contact_force":0.66387,"tcp_end":[0.45931,-0.01894,0.12759],"tcp_start":[0.46326,-0.01902,0.02713],"tcp_to_object_dist_end":0.01425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":730.0,"n_steps_budget":1000.0,"object_pos_end":[0.62182,0.15003,0.16728],"object_pos_start":[0.47182,-0.01949,0.1208],"object_to_goal_dist_end":0.02633,"object_to_goal_dist_start":0.24938,"object_z_max":0.16723,"peak_contact_force":0.07016,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28038.0,"raw_peak_contact_force":0.13071,"subtask_id":"transport_arc","tcp_end":[0.61863,0.14875,0.17841],"tcp_start":[0.45931,-0.01894,0.12759],"tcp_to_object_dist_end":0.01165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.62861,0.15837,0.17997],"object_pos_start":[0.62182,0.15003,0.16728],"object_to_goal_dist_end":0.01046,"object_to_goal_dist_start":0.02633,"object_z_max":0.17993,"peak_contact_force":0.0704,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.23558,"subtask_id":"release_1","tcp_end":[0.62642,0.15718,0.19224],"tcp_start":[0.61863,0.14875,0.17841],"tcp_to_object_dist_end":0.01252,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69663,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13494,"approach_1.approach_tolerance":0.02963,"descend_1.descend_speed":0.03674,"descend_1.descend_tolerance":0.00953,"descend_place.place_speed":0.05228,"descend_place.place_tolerance":0.01698,"descend_place.place_z_offset":0.01361,"lift_1.lift_height":0.13253,"lift_1.lift_speed":0.07025,"lift_1.lift_tolerance":0.01973,"transport_1.transport_speed":0.25037,"transport_1.transport_tolerance":0.01505},"optimized_scores":{"best_composite_score":0.26096,"best_fitness_score":0.98096,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45543,-0.02398,-0.00143],"force_p95":0.62573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67822,"mean_force":0.1469,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44545,-0.02468,0.02849]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6318.0,"contact_point_centroid":[0.44236,-0.04381,0.08536],"force_p95":0.08008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29771,"mean_force":0.05758,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44311,-0.02461,0.08265]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7563.0,"contact_point_centroid":[0.44421,-0.0056,0.08349],"force_p95":0.07589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28606,"mean_force":0.04939,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44311,-0.02461,0.082]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45864,-0.0262,-0.00215],"force_p95":0.16605,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24013,"mean_force":0.13396,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44791,-0.02475,0.02796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4260.0,"contact_point_centroid":[0.60251,0.20355,0.11541],"force_p95":0.07071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18034,"mean_force":0.04879,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60719,0.18528,0.11181]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4260.0,"contact_point_centroid":[0.61187,0.1666,0.11199],"force_p95":0.07346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15888,"mean_force":0.05045,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60719,0.18528,0.11181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5242.0,"contact_point_centroid":[0.44756,-0.00564,0.0282],"force_p95":0.06605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14771,"mean_force":0.0413,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44672,-0.02472,0.02685]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48019,-0.01111,0.18173]},{"body_a":"world","body_b":"grasp_target","contact_count":328.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45649,-0.02387,0.04621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19519.0,"contact_point_centroid":[0.52451,0.05897,0.12399],"force_p95":0.07398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10816,"mean_force":0.05115,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52212,0.07797,0.1227]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20328.0,"contact_point_centroid":[0.5177,0.09357,0.12567],"force_p95":0.07037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1018,"mean_force":0.04855,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51954,0.07471,0.12317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4503.0,"contact_point_centroid":[0.44598,-0.04403,0.02959],"force_p95":0.07928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08488,"mean_force":0.04918,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44673,-0.02472,0.02685]}],"total_contact_groups":12},"final_pose_error":0.01691,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61427,0.19984,0.1064],"final_tcp_position":[0.62013,0.20054,0.11646],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.67822,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46032,-0.02291,0.05931],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":328.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45497,-0.0249,0.03466],"tcp_start":[0.46032,-0.02291,0.05931],"tcp_to_object_dist_end":0.00947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02517,0.02548],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30296,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16278,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11545.0,"raw_peak_contact_force":0.24013,"subtask_id":"grasp_1","tcp_end":[0.4467,-0.02471,0.02682],"tcp_start":[0.45497,-0.0249,0.03466],"tcp_to_object_dist_end":0.01188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":351.0,"n_steps_budget":840.0,"object_pos_end":[0.45538,-0.02527,0.13639],"object_pos_start":[0.45849,-0.02517,0.02548],"object_to_goal_dist_end":0.29249,"object_to_goal_dist_start":0.30296,"object_z_max":0.13611,"peak_contact_force":0.07737,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13959.0,"raw_peak_contact_force":0.67822,"tcp_end":[0.4431,-0.0246,0.14018],"tcp_start":[0.4467,-0.02471,0.02682],"tcp_to_object_dist_end":0.01287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58734,0.16723,0.10207],"object_pos_start":[0.45538,-0.02527,0.13639],"object_to_goal_dist_end":0.06046,"object_to_goal_dist_start":0.29249,"object_z_max":0.13671,"peak_contact_force":0.07373,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39847.0,"raw_peak_contact_force":0.10816,"subtask_id":"transport_arc","tcp_end":[0.59467,0.16837,0.11059],"tcp_start":[0.4431,-0.0246,0.14018],"tcp_to_object_dist_end":0.0113,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.61427,0.19984,0.1064],"object_pos_start":[0.58734,0.16723,0.10207],"object_to_goal_dist_end":0.01952,"object_to_goal_dist_start":0.06046,"object_z_max":0.10637,"peak_contact_force":0.07318,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8520.0,"raw_peak_contact_force":0.18034,"subtask_id":"release_1","tcp_end":[0.62013,0.20054,0.11646],"tcp_start":[0.59467,0.16837,0.11059],"tcp_to_object_dist_end":0.01166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```