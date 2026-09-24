## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2591 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1466 | 0.44 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1891 | 0.42 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0465 | 0.16 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | force_threshold_switch | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.0704 | 0.16 | ❌ rejected |

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
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2569 |
| descend_1 | 1.00 | 1.00 | 0.0147 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1076 |
| transport_1 | 1.00 | 1.00 | 0.2346 |
| descend_place | 1.00 | 1.00 | 0.0176 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, 0.000, 0.047) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 27.129 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, 0.000, 0.047)→(0.474, -0.000, 0.033) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.033)→(0.465, -0.000, 0.024) | (0.479, -0.000, 0.026)→(0.478, -0.001, 0.025) | 0.278→0.279 | 1.00 / 44.000 | 0.167 | 0.254 |
| lift_1 | lift | 1.00 / step_budget | (0.465, -0.000, 0.024)→(0.462, -0.001, 0.132) | (0.478, -0.001, 0.025)→(0.475, -0.001, 0.128) | 0.279→0.251 | 1.00 / 38.333 | 0.089 | 0.812 |
| transport_1 | approach | 1.00 / step_budget | (0.462, -0.001, 0.132)→(0.595, 0.187, 0.141) | (0.475, -0.001, 0.128)→(0.600, 0.189, 0.133) | 0.251→0.026 | 1.00 / 36.000 | 0.086 | 0.132 |
| descend_place | descend | 1.00 / step_budget | (0.595, 0.187, 0.141)→(0.603, 0.200, 0.150) | (0.600, 0.189, 0.133)→(0.607, 0.203, 0.140) | 0.026→0.013 | 1.00 / 36.000 | 0.086 | 0.277 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.381
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.754
- phase_breakdown.release_1_score: 0.895
- phase_breakdown.approach_1_score: 0.557
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.678
- phase_breakdown.descend_1_score: 0.692
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
- **Final σ (mean)**: 0.297


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56213,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09243,"approach_1.approach_tolerance":0.00948,"descend_1.descend_speed":0.06409,"descend_1.descend_tolerance":0.00773,"descend_place.place_speed":0.08035,"descend_place.place_tolerance":0.01209,"descend_place.place_z_offset":0.01232,"lift_1.lift_height":0.13466,"lift_1.lift_speed":0.10233,"lift_1.lift_tolerance":0.00608,"transport_1.transport_speed":0.1207,"transport_1.transport_tolerance":0.02944},"optimized_scores":{"best_composite_score":0.25683,"best_fitness_score":0.97683,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":235.0,"contact_point_centroid":[0.49683,0.04181,-0.00148],"force_p95":0.566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93828,"mean_force":0.14166,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48455,0.04225,0.02348]},{"body_a":"grasp_target","body_b":"hand","contact_count":149.0,"contact_point_centroid":[0.51014,0.06209,0.06255],"force_p95":0.12215,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52904,"mean_force":0.0697,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48324,0.04214,0.02896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3264.0,"contact_point_centroid":[0.55169,0.25036,0.14644],"force_p95":0.11475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40065,"mean_force":0.08661,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55474,0.2316,0.14312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13596.0,"contact_point_centroid":[0.48293,0.06129,0.08326],"force_p95":0.09841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34328,"mean_force":0.06091,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48248,0.04207,0.08079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16238.0,"contact_point_centroid":[0.48474,0.02331,0.08003],"force_p95":0.08215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29954,"mean_force":0.05008,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48247,0.04207,0.07857]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50122,0.04459,-0.00235],"force_p95":0.19441,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29817,"mean_force":0.14881,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48796,0.04256,0.02281]},{"body_a":"grasp_target","body_b":"hand","contact_count":358.0,"contact_point_centroid":[0.51355,0.04999,0.05512],"force_p95":0.18383,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24269,"mean_force":0.05628,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48696,0.04248,0.02177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4329.0,"contact_point_centroid":[0.5632,0.21508,0.14171],"force_p95":0.09296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24239,"mean_force":0.06233,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55474,0.23159,0.14312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4341.0,"contact_point_centroid":[0.51582,0.14943,0.14183],"force_p95":0.11457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17012,"mean_force":0.07942,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51592,0.13025,0.13987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6033.0,"contact_point_centroid":[0.52037,0.10884,0.13956],"force_p95":0.10166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15821,"mean_force":0.06232,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51445,0.12642,0.13997]},{"body_a":"world","body_b":"grasp_target","contact_count":3396.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.497,0.02112,0.16747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.48836,0.0235,0.02315],"force_p95":0.06555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13221,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48671,0.04246,0.02151]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49537,0.04273,0.03425]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4341.0,"contact_point_centroid":[0.487,0.06195,0.0242],"force_p95":0.08555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10809,"mean_force":0.05299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48672,0.04246,0.02153]}],"total_contact_groups":14},"final_pose_error":0.01206,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5716,0.24607,0.13706],"final_tcp_position":[0.55904,0.24048,0.14923],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.93828,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3396.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49629,0.04246,0.03758],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":37.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":148.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49526,0.04317,0.03044],"tcp_start":[0.49629,0.04246,0.03758],"tcp_to_object_dist_end":0.00762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50086,0.04299,0.02489],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24423,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.18678,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11532.0,"raw_peak_contact_force":0.29817,"subtask_id":"grasp_1","tcp_end":[0.48669,0.04245,0.02149],"tcp_start":[0.49526,0.04317,0.03044],"tcp_to_object_dist_end":0.01459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.49741,0.04309,0.13784],"object_pos_start":[0.50086,0.04299,0.02489],"object_to_goal_dist_end":0.2128,"object_to_goal_dist_start":0.24423,"object_z_max":0.13773,"peak_contact_force":0.11294,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30218.0,"raw_peak_contact_force":0.93828,"tcp_end":[0.48276,0.0421,0.14415],"tcp_start":[0.48669,0.04245,0.02149],"tcp_to_object_dist_end":0.01598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.56539,0.22527,0.12983],"object_pos_start":[0.49741,0.04309,0.13784],"object_to_goal_dist_end":0.02592,"object_to_goal_dist_start":0.2128,"object_z_max":0.13788,"peak_contact_force":0.11514,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10374.0,"raw_peak_contact_force":0.17012,"subtask_id":"transport_arc","tcp_end":[0.55151,0.21992,0.13911],"tcp_start":[0.48276,0.0421,0.14415],"tcp_to_object_dist_end":0.01753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.5716,0.24607,0.13706],"object_pos_start":[0.56539,0.22527,0.12983],"object_to_goal_dist_end":0.01215,"object_to_goal_dist_start":0.02592,"object_z_max":0.13703,"peak_contact_force":0.11583,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7593.0,"raw_peak_contact_force":0.40065,"subtask_id":"release_1","tcp_end":[0.55904,0.24048,0.14923],"tcp_start":[0.55151,0.21992,0.13911],"tcp_to_object_dist_end":0.01836,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15529,"approach_1.approach_tolerance":0.01539,"descend_1.descend_speed":0.03471,"descend_1.descend_tolerance":0.0109,"descend_place.place_speed":0.05288,"descend_place.place_tolerance":0.0173,"descend_place.place_z_offset":0.01118,"lift_1.lift_height":0.1258,"lift_1.lift_speed":0.08344,"lift_1.lift_tolerance":0.01675,"transport_1.transport_speed":0.16519,"transport_1.transport_tolerance":0.0235},"optimized_scores":{"best_composite_score":0.25944,"best_fitness_score":0.97944,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47306,-0.01861,-0.00135],"force_p95":0.60268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70374,"mean_force":0.13999,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46217,-0.01897,0.02907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7515.0,"contact_point_centroid":[0.45885,-0.03811,0.0836],"force_p95":0.07845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32279,"mean_force":0.05833,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45951,-0.01892,0.08096]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9036.0,"contact_point_centroid":[0.46059,8e-05,0.08352],"force_p95":0.07433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31665,"mean_force":0.04992,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45952,-0.01892,0.08184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.61517,0.16881,0.18449],"force_p95":0.07014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23072,"mean_force":0.04904,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61929,0.15029,0.18144]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4762,-0.02007,-0.0021],"force_p95":0.15317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21845,"mean_force":0.13045,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46457,-0.01901,0.02875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.62315,0.13145,0.18216],"force_p95":0.07042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18568,"mean_force":0.04942,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61929,0.15029,0.18144]},{"body_a":"world","body_b":"grasp_target","contact_count":2324.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48598,-0.00912,0.17309]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.46452,8e-05,0.0291],"force_p95":0.06567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13198,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46336,-0.01899,0.02757]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4722,-0.01881,0.04073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11149.0,"contact_point_centroid":[0.54219,0.04788,0.15819],"force_p95":0.0806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12189,"mean_force":0.05374,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53966,0.06686,0.15664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11151.0,"contact_point_centroid":[0.53775,0.08507,0.15907],"force_p95":0.07853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11654,"mean_force":0.05296,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53903,0.06617,0.1565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4470.0,"contact_point_centroid":[0.46292,-0.03827,0.03031],"force_p95":0.07661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08578,"mean_force":0.04911,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46337,-0.01899,0.02758]}],"total_contact_groups":12},"final_pose_error":0.01718,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62746,0.15576,0.17813],"final_tcp_position":[0.62348,0.1544,0.18673],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.70374,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2324.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47357,-0.0186,0.04494],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":34.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":136.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.47176,-0.01909,0.03589],"tcp_start":[0.47357,-0.0186,0.04494],"tcp_to_object_dist_end":0.01086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01938,0.02565],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28817,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15131,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11302.0,"raw_peak_contact_force":0.21845,"subtask_id":"grasp_1","tcp_end":[0.46333,-0.01899,0.02754],"tcp_start":[0.47176,-0.01909,0.03589],"tcp_to_object_dist_end":0.01287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":425.0,"n_steps_budget":810.0,"object_pos_end":[0.47183,-0.01958,0.13181],"object_pos_start":[0.47606,-0.01938,0.02565],"object_to_goal_dist_end":0.24661,"object_to_goal_dist_start":0.28817,"object_z_max":0.1316,"peak_contact_force":0.07791,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16637.0,"raw_peak_contact_force":0.70374,"tcp_end":[0.45953,-0.01891,0.13703],"tcp_start":[0.46333,-0.01899,0.02754],"tcp_to_object_dist_end":0.01338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.61942,0.14718,0.16962],"object_pos_start":[0.47183,-0.01958,0.13181],"object_to_goal_dist_end":0.02654,"object_to_goal_dist_start":0.24661,"object_z_max":0.16956,"peak_contact_force":0.07031,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22300.0,"raw_peak_contact_force":0.12189,"subtask_id":"transport_arc","tcp_end":[0.6162,0.14607,0.17819],"tcp_start":[0.45953,-0.01891,0.13703],"tcp_to_object_dist_end":0.00923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":92.0,"n_steps_budget":1000.0,"object_pos_end":[0.62746,0.15576,0.17813],"object_pos_start":[0.61942,0.14718,0.16962],"object_to_goal_dist_end":0.01299,"object_to_goal_dist_start":0.02654,"object_z_max":0.17802,"peak_contact_force":0.07011,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3680.0,"raw_peak_contact_force":0.23072,"subtask_id":"release_1","tcp_end":[0.62348,0.1544,0.18673],"tcp_start":[0.6162,0.14607,0.17819],"tcp_to_object_dist_end":0.00957,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64641,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11469,"approach_1.approach_tolerance":0.02927,"descend_1.descend_speed":0.05455,"descend_1.descend_tolerance":0.00753,"descend_place.place_speed":0.09394,"descend_place.place_tolerance":0.00691,"descend_place.place_z_offset":0.00907,"lift_1.lift_height":0.10929,"lift_1.lift_speed":0.04708,"lift_1.lift_tolerance":0.01936,"transport_1.transport_speed":0.19276,"transport_1.transport_tolerance":0.01968},"optimized_scores":{"best_composite_score":0.26101,"best_fitness_score":0.98101,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.45521,-0.02433,-0.00152],"force_p95":0.72465,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79517,"mean_force":0.19324,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44515,-0.0249,0.02596]},{"body_a":"grasp_target","body_b":"hand","contact_count":128.0,"contact_point_centroid":[0.47373,-0.04509,0.07416],"force_p95":0.1175,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48192,"mean_force":0.0587,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44326,-0.02485,0.04332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5130.0,"contact_point_centroid":[0.44178,-0.04403,0.07136],"force_p95":0.07916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29915,"mean_force":0.05782,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44276,-0.02484,0.06864]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6270.0,"contact_point_centroid":[0.44361,-0.00581,0.07005],"force_p95":0.07449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27697,"mean_force":0.04864,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44276,-0.02484,0.06864]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45847,-0.02614,-0.00223],"force_p95":0.167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24572,"mean_force":0.13952,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44754,-0.02497,0.02547]},{"body_a":"grasp_target","body_b":"hand","contact_count":353.0,"contact_point_centroid":[0.47742,-0.03276,0.05526],"force_p95":0.0909,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22347,"mean_force":0.04628,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44656,-0.02495,0.02456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18100.0,"contact_point_centroid":[0.61491,0.21961,0.11082],"force_p95":0.06865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20002,"mean_force":0.047,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61993,0.20146,0.10704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18100.0,"contact_point_centroid":[0.62484,0.18285,0.10702],"force_p95":0.07166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17139,"mean_force":0.04908,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61993,0.20146,0.10704]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48013,-0.01113,0.1815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5198.0,"contact_point_centroid":[0.44721,-0.00588,0.02572],"force_p95":0.06407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12554,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44634,-0.02494,0.02436]},{"body_a":"world","body_b":"grasp_target","contact_count":424.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45608,-0.02401,0.04444]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16577.0,"contact_point_centroid":[0.53509,0.07196,0.10953],"force_p95":0.07494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10363,"mean_force":0.05166,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53248,0.09096,0.10824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17544.0,"contact_point_centroid":[0.52687,0.10545,0.11111],"force_p95":0.07069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09849,"mean_force":0.04815,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52905,0.08667,0.10837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4490.0,"contact_point_centroid":[0.44562,-0.04426,0.02709],"force_p95":0.07902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09348,"mean_force":0.04966,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44635,-0.02494,0.02436]}],"total_contact_groups":14},"final_pose_error":0.01111,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62287,0.20648,0.10424],"final_tcp_position":[0.62499,0.20619,0.11355],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":81.14225,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46024,-0.02294,0.05899],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":424.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45456,-0.02513,0.03209],"tcp_start":[0.46024,-0.02294,0.05899],"tcp_to_object_dist_end":0.00737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45813,-0.02533,0.02524],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30336,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16304,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11841.0,"raw_peak_contact_force":0.24572,"subtask_id":"grasp_1","tcp_end":[0.44632,-0.02494,0.02433],"tcp_start":[0.45456,-0.02513,0.03209],"tcp_to_object_dist_end":0.01185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":285.0,"n_steps_budget":690.0,"object_pos_end":[0.45443,-0.02543,0.11374],"object_pos_start":[0.45813,-0.02533,0.02524],"object_to_goal_dist_end":0.29234,"object_to_goal_dist_start":0.30336,"object_z_max":0.11346,"peak_contact_force":0.07668,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11606.0,"raw_peak_contact_force":0.79517,"tcp_end":[0.44252,-0.02482,0.11463],"tcp_start":[0.44632,-0.02494,0.02433],"tcp_to_object_dist_end":0.01196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.61377,0.19585,0.09988],"object_pos_start":[0.45443,-0.02543,0.11374],"object_to_goal_dist_end":0.02497,"object_to_goal_dist_start":0.29234,"object_z_max":0.11404,"peak_contact_force":0.07155,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34121.0,"raw_peak_contact_force":0.10363,"subtask_id":"transport_arc","tcp_end":[0.61729,0.1963,0.10567],"tcp_start":[0.44252,-0.02482,0.11463],"tcp_to_object_dist_end":0.0068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.62287,0.20648,0.10424],"object_pos_start":[0.61377,0.19585,0.09988],"object_to_goal_dist_end":0.01238,"object_to_goal_dist_start":0.02497,"object_z_max":0.10424,"peak_contact_force":0.07169,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36200.0,"raw_peak_contact_force":0.20002,"subtask_id":"release_1","tcp_end":[0.62499,0.20619,0.11355],"tcp_start":[0.61729,0.1963,0.10567],"tcp_to_object_dist_end":0.00955,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```