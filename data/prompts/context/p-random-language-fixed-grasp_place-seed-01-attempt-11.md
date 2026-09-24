## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2590 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2590 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ✅ accepted |

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
| approach_1 | 1.00 | 1.00 | 0.2579 |
| descend_1 | 1.00 | 1.00 | 0.0129 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1120 |
| transport_1 | 1.00 | 1.00 | 0.2433 |
| descend_place | 1.00 | 1.00 | 0.0253 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, 0.000, 0.046) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, 0.000, 0.046)→(0.474, -0.001, 0.034) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.034)→(0.465, -0.001, 0.025) | (0.479, -0.000, 0.026)→(0.478, -0.001, 0.025) | 0.278→0.279 | 1.00 / 43.000 | 0.170 | 0.251 |
| lift_1 | lift | 1.00 / step_budget | (0.465, -0.001, 0.025)→(0.462, -0.001, 0.137) | (0.478, -0.001, 0.025)→(0.474, -0.001, 0.132) | 0.279→0.251 | 1.00 / 36.667 | 0.092 | 0.762 |
| transport_1 | approach | 1.00 / step_budget | (0.462, -0.001, 0.137)→(0.599, 0.195, 0.142) | (0.474, -0.001, 0.132)→(0.598, 0.196, 0.130) | 0.251→0.026 | 1.00 / 38.667 | 0.080 | 0.136 |
| descend_place | descend | 1.00 / step_budget | (0.599, 0.195, 0.142)→(0.604, 0.202, 0.165) | (0.598, 0.196, 0.130)→(0.603, 0.203, 0.151) | 0.026→0.007 | 1.00 / 38.333 | 0.080 | 0.212 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.423
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.744
- phase_breakdown.release_1_score: 0.699
- phase_breakdown.approach_1_score: 0.607
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.710
- phase_breakdown.descend_1_score: 0.684
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
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57059,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16394,"approach_1.approach_tolerance":0.01052,"descend_1.descend_speed":0.09911,"descend_1.descend_tolerance":0.00985,"descend_place.place_speed":0.07789,"descend_place.place_tolerance":0.01366,"descend_place.place_z_offset":0.02998,"lift_1.lift_height":0.13604,"lift_1.lift_speed":0.04956,"lift_1.lift_tolerance":0.01327,"transport_1.transport_speed":0.2246,"transport_1.transport_tolerance":0.01469},"optimized_scores":{"best_composite_score":0.25678,"best_fitness_score":0.97678,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":122.0,"contact_point_centroid":[0.49763,0.04036,-0.00151],"force_p95":0.50065,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78416,"mean_force":0.11598,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48531,0.0419,0.0266]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11757.0,"contact_point_centroid":[0.48365,0.06092,0.09003],"force_p95":0.10881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42734,"mean_force":0.06246,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48266,0.04167,0.08754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14362.0,"contact_point_centroid":[0.48503,0.02311,0.08644],"force_p95":0.09015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31929,"mean_force":0.05081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48267,0.04168,0.08505]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50141,0.04478,-0.00229],"force_p95":0.2044,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28581,"mean_force":0.14438,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48806,0.04215,0.02591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4043.0,"contact_point_centroid":[0.55243,0.25667,0.15548],"force_p95":0.09597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25016,"mean_force":0.06028,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55744,0.23845,0.15125]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5160.0,"contact_point_centroid":[0.48843,0.02321,0.02629],"force_p95":0.06751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20301,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48681,0.04204,0.02462]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5060.0,"contact_point_centroid":[0.56428,0.22088,0.15062],"force_p95":0.08529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18464,"mean_force":0.04927,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55744,0.23845,0.15126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10765.0,"contact_point_centroid":[0.51909,0.16127,0.14359],"force_p95":0.11711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1752,"mean_force":0.07958,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51995,0.14219,0.1414]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15518.0,"contact_point_centroid":[0.52559,0.12424,0.14107],"force_p95":0.09301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16846,"mean_force":0.05654,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51985,0.14187,0.14144]},{"body_a":"world","body_b":"grasp_target","contact_count":3152.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49706,0.02096,0.16851]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49547,0.04243,0.0365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.4877,0.06155,0.02754],"force_p95":0.09517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10932,"mean_force":0.05822,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48683,0.04205,0.02463]}],"total_contact_groups":12},"final_pose_error":0.01357,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56357,0.24495,0.14693],"final_tcp_position":[0.55975,0.24204,0.16433],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.78416,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3152.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49634,0.04226,0.03882],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":100.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49538,0.04275,0.03362],"tcp_start":[0.49634,0.04226,0.03882],"tcp_to_object_dist_end":0.00984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50138,0.04283,0.02501],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24417,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19494,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11052.0,"raw_peak_contact_force":0.28581,"subtask_id":"grasp_1","tcp_end":[0.48679,0.04204,0.02459],"tcp_start":[0.49538,0.04275,0.03362],"tcp_to_object_dist_end":0.01462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":699.0,"n_steps_budget":870.0,"object_pos_end":[0.49691,0.04263,0.13965],"object_pos_start":[0.50138,0.04283,0.02501],"object_to_goal_dist_end":0.21332,"object_to_goal_dist_start":0.24417,"object_z_max":0.13952,"peak_contact_force":0.11833,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26241.0,"raw_peak_contact_force":0.78416,"tcp_end":[0.48291,0.0417,0.14808],"tcp_start":[0.48679,0.04204,0.02459],"tcp_to_object_dist_end":0.01637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.56169,0.23773,0.12295],"object_pos_start":[0.49691,0.04263,0.13965],"object_to_goal_dist_end":0.02502,"object_to_goal_dist_start":0.21332,"object_z_max":0.13969,"peak_contact_force":0.09816,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26283.0,"raw_peak_contact_force":0.1752,"subtask_id":"transport_arc","tcp_end":[0.55705,0.23475,0.13932],"tcp_start":[0.48291,0.0417,0.14808],"tcp_to_object_dist_end":0.01728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.56357,0.24495,0.14693],"object_pos_start":[0.56169,0.23773,0.12295],"object_to_goal_dist_end":0.00086,"object_to_goal_dist_start":0.02502,"object_z_max":0.14685,"peak_contact_force":0.09726,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9103.0,"raw_peak_contact_force":0.25016,"subtask_id":"release_1","tcp_end":[0.55975,0.24204,0.16433],"tcp_start":[0.55705,0.23475,0.13932],"tcp_to_object_dist_end":0.01805,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10181,"approach_1.approach_tolerance":0.0156,"descend_1.descend_speed":0.05491,"descend_1.descend_tolerance":0.01077,"descend_place.place_speed":0.04575,"descend_place.place_tolerance":0.01227,"descend_place.place_z_offset":0.02181,"lift_1.lift_height":0.12663,"lift_1.lift_speed":0.0631,"lift_1.lift_tolerance":0.01327,"transport_1.transport_speed":0.15599,"transport_1.transport_tolerance":0.01649},"optimized_scores":{"best_composite_score":0.25943,"best_fitness_score":0.97943,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":105.0,"contact_point_centroid":[0.47291,-0.01828,-0.00131],"force_p95":0.49735,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70731,"mean_force":0.11467,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46203,-0.01898,0.02898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10793.0,"contact_point_centroid":[0.45905,-0.03812,0.08708],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32326,"mean_force":0.05754,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45931,-0.01892,0.08437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13051.0,"contact_point_centroid":[0.4605,7e-05,0.08588],"force_p95":0.07306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31704,"mean_force":0.04896,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45929,-0.01892,0.08401]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4762,-0.02007,-0.0021],"force_p95":0.15299,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2172,"mean_force":0.13038,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46454,-0.01902,0.02859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7300.0,"contact_point_centroid":[0.61922,0.17336,0.19276],"force_p95":0.06899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2058,"mean_force":0.04756,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62347,0.15487,0.18969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7300.0,"contact_point_centroid":[0.62741,0.13604,0.1904],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1746,"mean_force":0.04867,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62347,0.15487,0.18969]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48599,-0.00912,0.17311]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.46449,7e-05,0.02894],"force_p95":0.06564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13169,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46333,-0.019,0.02741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18669.0,"contact_point_centroid":[0.54643,0.05268,0.16135],"force_p95":0.07639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13026,"mean_force":0.0516,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54384,0.07167,0.15991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18602.0,"contact_point_centroid":[0.54195,0.09016,0.16239],"force_p95":0.07723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12639,"mean_force":0.05122,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54347,0.07126,0.15985]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4722,-0.01881,0.04072]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4468.0,"contact_point_centroid":[0.4629,-0.03828,0.03015],"force_p95":0.07659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08548,"mean_force":0.04913,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46334,-0.019,0.02741]}],"total_contact_groups":12},"final_pose_error":0.01226,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.6258,0.15821,0.18507],"final_tcp_position":[0.62695,0.1576,0.20052],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.70731,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4736,-0.01859,0.0451],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":35.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":140.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.47173,-0.0191,0.03574],"tcp_start":[0.4736,-0.01859,0.0451],"tcp_to_object_dist_end":0.01073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01938,0.02565],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28817,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15116,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11300.0,"raw_peak_contact_force":0.2172,"subtask_id":"grasp_1","tcp_end":[0.4633,-0.019,0.02738],"tcp_start":[0.47173,-0.0191,0.03574],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":611.0,"n_steps_budget":810.0,"object_pos_end":[0.4715,-0.01951,0.13353],"object_pos_start":[0.47606,-0.01938,0.02565],"object_to_goal_dist_end":0.24637,"object_to_goal_dist_start":0.28817,"object_z_max":0.13339,"peak_contact_force":0.0807,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23949.0,"raw_peak_contact_force":0.70731,"tcp_end":[0.45944,-0.01892,0.14138],"tcp_start":[0.4633,-0.019,0.02738],"tcp_to_object_dist_end":0.0144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.61989,0.152,0.16583],"object_pos_start":[0.4715,-0.01951,0.13353],"object_to_goal_dist_end":0.02774,"object_to_goal_dist_start":0.24637,"object_z_max":0.16581,"peak_contact_force":0.07043,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37271.0,"raw_peak_contact_force":0.13026,"subtask_id":"transport_arc","tcp_end":[0.62116,0.1515,0.17981],"tcp_start":[0.45944,-0.01892,0.14138],"tcp_to_object_dist_end":0.01405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.6258,0.15821,0.18507],"object_pos_start":[0.61989,0.152,0.16583],"object_to_goal_dist_end":0.00755,"object_to_goal_dist_start":0.02774,"object_z_max":0.18503,"peak_contact_force":0.07068,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14600.0,"raw_peak_contact_force":0.2058,"subtask_id":"release_1","tcp_end":[0.62695,0.1576,0.20052],"tcp_start":[0.62116,0.1515,0.17981],"tcp_to_object_dist_end":0.0155,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70652,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09589,"approach_1.approach_tolerance":0.02526,"descend_1.descend_speed":0.05801,"descend_1.descend_tolerance":0.00708,"descend_place.place_speed":0.03677,"descend_place.place_tolerance":0.00977,"descend_place.place_z_offset":0.02733,"lift_1.lift_height":0.12214,"lift_1.lift_speed":0.08765,"lift_1.lift_tolerance":0.0243,"transport_1.transport_speed":0.05014,"transport_1.transport_tolerance":0.0173},"optimized_scores":{"best_composite_score":0.26084,"best_fitness_score":0.98084,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.45518,-0.02506,-0.0016],"force_p95":0.7317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7945,"mean_force":0.22666,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44485,-0.02496,0.0254]},{"body_a":"grasp_target","body_b":"hand","contact_count":146.0,"contact_point_centroid":[0.47348,-0.04522,0.083],"force_p95":0.12691,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48595,"mean_force":0.06445,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44299,-0.02491,0.05196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4284.0,"contact_point_centroid":[0.442,-0.04411,0.07417],"force_p95":0.07969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29456,"mean_force":0.05874,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4428,-0.0249,0.07147]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5201.0,"contact_point_centroid":[0.44376,-0.00588,0.07264],"force_p95":0.07578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2727,"mean_force":0.04978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4428,-0.0249,0.07119]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45841,-0.02615,-0.00226],"force_p95":0.16876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25014,"mean_force":0.14169,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44735,-0.02503,0.02493]},{"body_a":"grasp_target","body_b":"hand","contact_count":364.0,"contact_point_centroid":[0.47726,-0.03217,0.05497],"force_p95":0.09244,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21224,"mean_force":0.05921,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44643,-0.02501,0.02407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18100.0,"contact_point_centroid":[0.61581,0.22065,0.12125],"force_p95":0.06946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18002,"mean_force":0.04744,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6209,0.20252,0.11749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18100.0,"contact_point_centroid":[0.62584,0.18391,0.1175],"force_p95":0.0727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.155,"mean_force":0.04946,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6209,0.20252,0.11749]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47948,-0.01136,0.17907]},{"body_a":"world","body_b":"grasp_target","contact_count":392.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45566,-0.02424,0.04233]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5201.0,"contact_point_centroid":[0.44704,-0.00594,0.02518],"force_p95":0.06453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11156,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44616,-0.025,0.02382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19665.0,"contact_point_centroid":[0.53684,0.07403,0.11307],"force_p95":0.07348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10197,"mean_force":0.05125,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53413,0.09301,0.11186]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4480.0,"contact_point_centroid":[0.44545,-0.04432,0.02654],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09709,"mean_force":0.04979,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44617,-0.025,0.02382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20674.0,"contact_point_centroid":[0.52849,0.10751,0.11486],"force_p95":0.07074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09662,"mean_force":0.04807,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53072,0.08874,0.11213]}],"total_contact_groups":14},"final_pose_error":0.01139,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62082,0.20611,0.12062],"final_tcp_position":[0.62537,0.20643,0.13126],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.7945,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45929,-0.02335,0.05477],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":98.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":392.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45436,-0.02519,0.03152],"tcp_start":[0.45929,-0.02335,0.05477],"tcp_to_object_dist_end":0.00701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45801,-0.02537,0.02515],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30348,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16419,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11845.0,"raw_peak_contact_force":0.25014,"subtask_id":"grasp_1","tcp_end":[0.44614,-0.025,0.02379],"tcp_start":[0.45436,-0.02519,0.03152],"tcp_to_object_dist_end":0.01196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":238.0,"n_steps_budget":780.0,"object_pos_end":[0.45503,-0.02546,0.12216],"object_pos_start":[0.45801,-0.02537,0.02515],"object_to_goal_dist_end":0.29211,"object_to_goal_dist_start":0.30348,"object_z_max":0.12178,"peak_contact_force":0.07703,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9704.0,"raw_peak_contact_force":0.7945,"tcp_end":[0.44263,-0.02489,0.12214],"tcp_start":[0.44614,-0.025,0.02379],"tcp_to_object_dist_end":0.01241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61315,0.1973,0.09997],"object_pos_start":[0.45503,-0.02546,0.12216],"object_to_goal_dist_end":0.02465,"object_to_goal_dist_start":0.29211,"object_z_max":0.12282,"peak_contact_force":0.0727,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40339.0,"raw_peak_contact_force":0.10197,"subtask_id":"transport_arc","tcp_end":[0.61884,0.19832,0.10588],"tcp_start":[0.44263,-0.02489,0.12214],"tcp_to_object_dist_end":0.00826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.62082,0.20611,0.12062],"object_pos_start":[0.61315,0.1973,0.09997],"object_to_goal_dist_end":0.01154,"object_to_goal_dist_start":0.02465,"object_z_max":0.12061,"peak_contact_force":0.0727,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36200.0,"raw_peak_contact_force":0.18002,"subtask_id":"release_1","tcp_end":[0.62537,0.20643,0.13126],"tcp_start":[0.61884,0.19832,0.10588],"tcp_to_object_dist_end":0.01158,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```