## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2592 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2924 | 0.57 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2590 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2590 | 1.00 | ❌ rejected |

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
| approach_1 | 0.67 | 1.00 | 0.2324 |
| descend_1 | 1.00 | 1.00 | 0.0399 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1075 |
| transport_1 | 1.00 | 1.00 | 0.2351 |
| descend_place | 1.00 | 1.00 | 0.0215 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.003, 0.071) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, -0.003, 0.071)→(0.474, -0.000, 0.032) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.032)→(0.465, -0.001, 0.024) | (0.479, -0.000, 0.026)→(0.478, -0.001, 0.025) | 0.278→0.279 | 1.00 / 43.667 | 0.170 | 0.262 |
| lift_1 | lift | 1.00 / step_budget | (0.465, -0.001, 0.024)→(0.462, -0.001, 0.131) | (0.478, -0.001, 0.025)→(0.475, -0.001, 0.128) | 0.279→0.249 | 1.00 / 37.667 | 14.169 | 0.805 |
| transport_1 | approach | 1.00 / step_budget | (0.462, -0.001, 0.131)→(0.594, 0.189, 0.141) | (0.475, -0.001, 0.128)→(0.600, 0.191, 0.133) | 0.249→0.025 | 1.00 / 37.667 | 0.085 | 0.141 |
| descend_place | descend | 1.00 / step_budget | (0.594, 0.189, 0.141)→(0.603, 0.201, 0.155) | (0.600, 0.191, 0.133)→(0.608, 0.203, 0.145) | 0.025→0.010 | 1.00 / 38.000 | 0.080 | 0.244 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.502
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.724
- phase_breakdown.release_1_score: 0.827
- phase_breakdown.approach_1_score: 0.560
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.645
- phase_breakdown.descend_1_score: 0.677
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
- **Final σ (mean)**: 0.320


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76623,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14301,"approach_1.approach_tolerance":0.00502,"descend_1.descend_speed":0.04386,"descend_1.descend_tolerance":0.00716,"descend_place.place_speed":0.07334,"descend_place.place_tolerance":0.0144,"descend_place.place_z_offset":0.02119,"lift_1.lift_height":0.11832,"lift_1.lift_speed":0.09612,"lift_1.lift_tolerance":0.02349,"transport_1.transport_speed":0.20334,"transport_1.transport_tolerance":0.01853},"optimized_scores":{"best_composite_score":0.25711,"best_fitness_score":0.97711,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.49768,0.04191,-0.00175],"force_p95":0.82286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95536,"mean_force":0.23391,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4856,0.04216,0.02248]},{"body_a":"grasp_target","body_b":"hand","contact_count":161.0,"contact_point_centroid":[0.50913,0.06203,0.08353],"force_p95":0.12487,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54112,"mean_force":0.07065,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48354,0.04198,0.04972]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4250.0,"contact_point_centroid":[0.4834,0.0612,0.06971],"force_p95":0.08558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34059,"mean_force":0.0621,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48334,0.04197,0.06717]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50116,0.04453,-0.0024],"force_p95":0.20125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30775,"mean_force":0.153,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4882,0.04242,0.02211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5380.0,"contact_point_centroid":[0.48506,0.02303,0.06936],"force_p95":0.08099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29952,"mean_force":0.05032,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48333,0.04197,0.06773]},{"body_a":"grasp_target","body_b":"hand","contact_count":370.0,"contact_point_centroid":[0.51387,0.04925,0.05476],"force_p95":0.2062,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25232,"mean_force":0.07372,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48726,0.04233,0.02115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2597.0,"contact_point_centroid":[0.55251,0.2549,0.14902],"force_p95":0.09759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23338,"mean_force":0.06793,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55668,0.23643,0.14541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3450.0,"contact_point_centroid":[0.56398,0.21913,0.14515],"force_p95":0.08908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15753,"mean_force":0.05387,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55672,0.23651,0.14558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11031.0,"contact_point_centroid":[0.5156,0.15487,0.12754],"force_p95":0.10907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14021,"mean_force":0.06199,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51752,0.13587,0.12474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13137.0,"contact_point_centroid":[0.52394,0.12063,0.12563],"force_p95":0.08729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13873,"mean_force":0.05324,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51862,0.13857,0.12513]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49693,0.0168,0.19358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4779.0,"contact_point_centroid":[0.48886,0.02338,0.02224],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12927,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48694,0.04231,0.02081]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49448,0.03775,0.06155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4352.0,"contact_point_centroid":[0.4871,0.0618,0.0234],"force_p95":0.08535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10505,"mean_force":0.05323,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48696,0.04231,0.02083]}],"total_contact_groups":14},"final_pose_error":0.01432,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57238,0.24605,0.14899],"final_tcp_position":[0.55917,0.24104,0.1552],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.95536,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49632,0.0329,0.09567],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07087,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4955,0.04301,0.02973],"tcp_start":[0.49632,0.0329,0.09567],"tcp_to_object_dist_end":0.00709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50076,0.04281,0.02474],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24448,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19144,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11301.0,"raw_peak_contact_force":0.30775,"subtask_id":"grasp_1","tcp_end":[0.48692,0.0423,0.02079],"tcp_start":[0.4955,0.04301,0.02973],"tcp_to_object_dist_end":0.0144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":250.0,"n_steps_budget":750.0,"object_pos_end":[0.49735,0.04277,0.11863],"object_pos_start":[0.50076,0.04281,0.02474],"object_to_goal_dist_end":0.21479,"object_to_goal_dist_start":0.24448,"object_z_max":0.11829,"peak_contact_force":0.08346,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9870.0,"raw_peak_contact_force":0.95536,"tcp_end":[0.48312,0.04195,0.1163],"tcp_start":[0.48692,0.0423,0.02079],"tcp_to_object_dist_end":0.01444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.57047,0.23677,0.13328],"object_pos_start":[0.49735,0.04277,0.11863],"object_to_goal_dist_end":0.01686,"object_to_goal_dist_start":0.21479,"object_z_max":0.13326,"peak_contact_force":0.11254,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24168.0,"raw_peak_contact_force":0.14021,"subtask_id":"transport_arc","tcp_end":[0.55575,0.23154,0.13749],"tcp_start":[0.48312,0.04195,0.1163],"tcp_to_object_dist_end":0.01618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.57238,0.24605,0.14899],"object_pos_start":[0.57047,0.23677,0.13328],"object_to_goal_dist_end":0.00835,"object_to_goal_dist_start":0.01686,"object_z_max":0.1489,"peak_contact_force":0.09681,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6047.0,"raw_peak_contact_force":0.23338,"subtask_id":"release_1","tcp_end":[0.55917,0.24104,0.1552],"tcp_start":[0.55575,0.23154,0.13749],"tcp_to_object_dist_end":0.01544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69101,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13039,"approach_1.approach_tolerance":0.02999,"descend_1.descend_speed":0.0556,"descend_1.descend_tolerance":0.0106,"descend_place.place_speed":0.06213,"descend_place.place_tolerance":0.00996,"descend_place.place_z_offset":0.01049,"lift_1.lift_height":0.1494,"lift_1.lift_speed":0.04373,"lift_1.lift_tolerance":0.01668,"transport_1.transport_speed":0.23434,"transport_1.transport_tolerance":0.02907},"optimized_scores":{"best_composite_score":0.25948,"best_fitness_score":0.97948,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.4729,-0.01836,-0.00135],"force_p95":0.62689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66904,"mean_force":0.13491,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46207,-0.0189,0.02864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9181.0,"contact_point_centroid":[0.45893,-0.03805,0.09644],"force_p95":0.07878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30326,"mean_force":0.05764,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4595,-0.01885,0.09375]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11060.0,"contact_point_centroid":[0.46058,0.00015,0.09556],"force_p95":0.07337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29606,"mean_force":0.04918,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45949,-0.01885,0.09368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16620.0,"contact_point_centroid":[0.61558,0.16941,0.18677],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22884,"mean_force":0.04748,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61971,0.15089,0.18372]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47621,-0.02007,-0.00211],"force_p95":0.15553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22795,"mean_force":0.13103,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46454,-0.01894,0.02825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16620.0,"contact_point_centroid":[0.62357,0.13205,0.18444],"force_p95":0.07007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17569,"mean_force":0.04863,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61971,0.15089,0.18372]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48769,-0.00849,0.18201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8150.0,"contact_point_centroid":[0.53914,0.04407,0.16975],"force_p95":0.08252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12691,"mean_force":0.0542,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53668,0.06309,0.16819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5028.0,"contact_point_centroid":[0.46449,0.00015,0.02861],"force_p95":0.06605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12384,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46333,-0.01892,0.02707]},{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47258,-0.01824,0.04676]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8168.0,"contact_point_centroid":[0.5349,0.08134,0.1706],"force_p95":0.07903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.114,"mean_force":0.05319,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53607,0.06243,0.16814]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4474.0,"contact_point_centroid":[0.4629,-0.03821,0.02982],"force_p95":0.0764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.04912,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46333,-0.01892,0.02708]}],"total_contact_groups":12},"final_pose_error":0.01057,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62818,0.15845,0.18009],"final_tcp_position":[0.62692,0.15753,0.19109],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":42.34119,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47571,-0.01752,0.05961],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":296.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47173,-0.01902,0.03539],"tcp_start":[0.47571,-0.01752,0.05961],"tcp_to_object_dist_end":0.01043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01931,0.02562],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28814,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15332,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11302.0,"raw_peak_contact_force":0.22795,"subtask_id":"grasp_1","tcp_end":[0.4633,-0.01892,0.02704],"tcp_start":[0.47173,-0.01902,0.03539],"tcp_to_object_dist_end":0.01284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":514.0,"n_steps_budget":930.0,"object_pos_end":[0.47221,-0.01934,0.15439],"object_pos_start":[0.47606,-0.01931,0.02562],"object_to_goal_dist_end":0.24185,"object_to_goal_dist_start":0.28814,"object_z_max":0.15418,"peak_contact_force":42.34119,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20328.0,"raw_peak_contact_force":0.66904,"tcp_end":[0.45969,-0.01884,0.16017],"tcp_start":[0.4633,-0.01892,0.02704],"tcp_to_object_dist_end":0.01379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.61394,0.14197,0.17123],"object_pos_start":[0.47221,-0.01934,0.15439],"object_to_goal_dist_end":0.0309,"object_to_goal_dist_start":0.24185,"object_z_max":0.1712,"peak_contact_force":0.07037,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16318.0,"raw_peak_contact_force":0.12691,"subtask_id":"transport_arc","tcp_end":[0.61185,0.14118,0.17912],"tcp_start":[0.45969,-0.01884,0.16017],"tcp_to_object_dist_end":0.0082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.62818,0.15845,0.18009],"object_pos_start":[0.61394,0.14197,0.17123],"object_to_goal_dist_end":0.01047,"object_to_goal_dist_start":0.0309,"object_z_max":0.18008,"peak_contact_force":0.07041,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33240.0,"raw_peak_contact_force":0.22884,"subtask_id":"release_1","tcp_end":[0.62692,0.15753,0.19109],"tcp_start":[0.61185,0.14118,0.17912],"tcp_to_object_dist_end":0.01111,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69444,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09214,"approach_1.approach_tolerance":0.02949,"descend_1.descend_speed":0.07961,"descend_1.descend_tolerance":0.00668,"descend_place.place_speed":0.07022,"descend_place.place_tolerance":0.01528,"descend_place.place_z_offset":0.01848,"lift_1.lift_height":0.10489,"lift_1.lift_speed":0.0242,"lift_1.lift_tolerance":0.00521,"transport_1.transport_speed":0.14629,"transport_1.transport_tolerance":0.02209},"optimized_scores":{"best_composite_score":0.26099,"best_fitness_score":0.98099,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":226.0,"contact_point_centroid":[0.4548,-0.02461,-0.0014],"force_p95":0.40608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78988,"mean_force":0.11795,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44417,-0.02498,0.02537]},{"body_a":"grasp_target","body_b":"hand","contact_count":153.0,"contact_point_centroid":[0.47372,-0.04525,0.06247],"force_p95":0.11524,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4577,"mean_force":0.07054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44281,-0.02494,0.03153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10444.0,"contact_point_centroid":[0.44221,-0.04412,0.0695],"force_p95":0.08063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28507,"mean_force":0.05844,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4421,-0.02491,0.06691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3500.0,"contact_point_centroid":[0.61382,0.21779,0.11545],"force_p95":0.07004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2698,"mean_force":0.04784,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61883,0.19963,0.1117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12678.0,"contact_point_centroid":[0.44381,-0.00595,0.06815],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26923,"mean_force":0.04977,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44209,-0.02491,0.06663]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45834,-0.02616,-0.0023],"force_p95":0.17083,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25135,"mean_force":0.14425,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44741,-0.02507,0.02439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3500.0,"contact_point_centroid":[0.62373,0.18101,0.11171],"force_p95":0.07175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21787,"mean_force":0.04912,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61883,0.19963,0.1117]},{"body_a":"grasp_target","body_b":"hand","contact_count":373.0,"contact_point_centroid":[0.47723,-0.032,0.05469],"force_p95":0.09958,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20647,"mean_force":0.07133,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44654,-0.02505,0.02358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13321.0,"contact_point_centroid":[0.53374,0.06949,0.11059],"force_p95":0.10627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15661,"mean_force":0.05874,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53041,0.08834,0.1095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14096.0,"contact_point_centroid":[0.53008,0.10809,0.11198],"force_p95":0.09172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14121,"mean_force":0.05331,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53136,0.08952,0.10946]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48014,-0.01114,0.18145]},{"body_a":"world","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4559,-0.02408,0.0436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5203.0,"contact_point_centroid":[0.44707,-0.00598,0.02461],"force_p95":0.06485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11138,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44622,-0.02504,0.02327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4477.0,"contact_point_centroid":[0.44547,-0.04436,0.02599],"force_p95":0.07928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0958,"mean_force":0.04984,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44623,-0.02504,0.02328]}],"total_contact_groups":14},"final_pose_error":0.01523,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62359,0.20572,0.10704],"final_tcp_position":[0.62332,0.20443,0.11951],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.78988,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46022,-0.02297,0.05876],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":480.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4544,-0.02523,0.03096],"tcp_start":[0.46022,-0.02297,0.05876],"tcp_to_object_dist_end":0.00655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45791,-0.0254,0.02505],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30359,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16552,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11853.0,"raw_peak_contact_force":0.25135,"subtask_id":"grasp_1","tcp_end":[0.44619,-0.02504,0.02325],"tcp_start":[0.4544,-0.02523,0.03096],"tcp_to_object_dist_end":0.01186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.45638,-0.02568,0.11041],"object_pos_start":[0.45791,-0.0254,0.02505],"object_to_goal_dist_end":0.2914,"object_to_goal_dist_start":0.30359,"object_z_max":0.1103,"peak_contact_force":0.08154,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23501.0,"raw_peak_contact_force":0.78988,"tcp_end":[0.44219,-0.02491,0.11688],"tcp_start":[0.44619,-0.02504,0.02325],"tcp_to_object_dist_end":0.01562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.61511,0.19502,0.09382],"object_pos_start":[0.45638,-0.02568,0.11041],"object_to_goal_dist_end":0.02849,"object_to_goal_dist_start":0.2914,"object_z_max":0.11043,"peak_contact_force":0.07179,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27417.0,"raw_peak_contact_force":0.15661,"subtask_id":"transport_arc","tcp_end":[0.61555,0.19401,0.10587],"tcp_start":[0.44219,-0.02491,0.11688],"tcp_to_object_dist_end":0.0121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.62359,0.20572,0.10704],"object_pos_start":[0.61511,0.19502,0.09382],"object_to_goal_dist_end":0.00996,"object_to_goal_dist_start":0.02849,"object_z_max":0.10696,"peak_contact_force":0.07162,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7000.0,"raw_peak_contact_force":0.2698,"subtask_id":"release_1","tcp_end":[0.62332,0.20443,0.11951],"tcp_start":[0.61555,0.19401,0.10587],"tcp_to_object_dist_end":0.01254,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```