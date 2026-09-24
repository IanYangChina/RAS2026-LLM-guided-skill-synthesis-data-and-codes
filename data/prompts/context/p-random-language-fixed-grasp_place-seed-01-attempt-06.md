## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1466 | 0.44 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1891 | 0.42 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0465 | 0.16 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | force_threshold_switch | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.0704 | 0.16 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | force_threshold_switch | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.0465 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.147) — your mutation base

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
- id: descend_release_1
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
    offset_along_axis:
      distance: 0.03
      axis: world_z
      mode: add_to_offset
      sign: positive
  parameters:
    release_height_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    release_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale
  subtask_id: release_1
- id: release_1
  type: release
  control: impedance_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (scale)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (scale)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (scale)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_release_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.03, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - release_height_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - release_speed: status=consumed; consumers=generator.speed (scale)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.147
- **task_score** (E): 0.436
- **fitness_score**: 0.697  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2654 |
| descend_1 | 1.00 | 1.00 | 0.0046 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1209 |
| transport_1 | 1.00 | 1.00 | 0.2412 |
| descend_release_1 | 1.00 | 1.00 | 0.0275 |
| release_1 | 1.00 | 1.00 | 0.0214 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.475, -0.000, 0.039) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.475, -0.000, 0.039)→(0.474, -0.001, 0.034) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.034)→(0.465, -0.001, 0.026) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.278 | 1.00 / 42.667 | 0.167 | 0.245 |
| lift_1 | lift | 1.00 / step_budget | (0.465, -0.001, 0.026)→(0.462, -0.001, 0.147) | (0.479, -0.001, 0.025)→(0.474, -0.001, 0.138) | 0.278→0.252 | 1.00 / 36.333 | 0.093 | 0.733 |
| transport_1 | approach | 1.00 / step_budget | (0.462, -0.001, 0.147)→(0.597, 0.192, 0.142) | (0.474, -0.001, 0.138)→(0.597, 0.193, 0.127) | 0.252→0.030 | 1.00 / 36.667 | 0.087 | 0.147 |
| descend_release_1 | descend | 1.00 / step_budget | (0.597, 0.192, 0.142)→(0.604, 0.202, 0.166) | (0.597, 0.193, 0.127)→(0.604, 0.204, 0.145) | 0.030→0.009 | 1.00 / 35.667 | 0.098 | 0.306 |
| release_1 | release | 1.00 / step_budget | (0.604, 0.202, 0.166)→(0.599, 0.200, 0.187) | (0.604, 0.204, 0.145)→(0.603, 0.202, 0.023) | 0.009→0.128 | 1.00 / 4.000 | 0.112 | 1.424 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.557
- phase_score: 0.717
- phase_breakdown.release_1_score: 0.404
- phase_breakdown.approach_1_score: 0.821
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.713
- phase_breakdown.descend_1_score: 0.735
- grasp_place_fitness: 0.759

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.759
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.557
- **Median Q (composite search score)**: 0.136
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.262


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55758,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14424,"descend_1.descend_speed":0.06269,"descend_release_1.release_height_offset":0.02426,"descend_release_1.release_speed":0.07107,"lift_1.lift_height":0.10742,"release_1.release_duration":0.29473,"transport_1.transport_speed":0.05566,"transport_1.transport_tolerance":0.02066},"optimized_scores":{"best_composite_score":0.13618,"best_fitness_score":0.68618,"best_task_score":0.4188},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":390.0,"contact_point_centroid":[0.5686,0.24536,-0.00427],"force_p95":1.00136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58842,"mean_force":0.23333,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55492,0.24041,0.16976]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.49759,0.04049,-0.00141],"force_p95":0.48622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78413,"mean_force":0.10979,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48509,0.0419,0.02683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9967.0,"contact_point_centroid":[0.48377,0.06092,0.07544],"force_p95":0.10743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42755,"mean_force":0.06334,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48257,0.04168,0.07261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8989.0,"contact_point_centroid":[0.5536,0.25512,0.14989],"force_p95":0.1517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40928,"mean_force":0.09256,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.55625,0.23611,0.1483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12474.0,"contact_point_centroid":[0.48491,0.0231,0.07182],"force_p95":0.08995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31963,"mean_force":0.05065,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48259,0.04169,0.07042]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50141,0.04479,-0.00229],"force_p95":0.2039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28544,"mean_force":0.14424,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48805,0.04217,0.02593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.55966,0.26262,0.15822],"force_p95":0.21488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28028,"mean_force":0.18114,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55956,0.24245,0.16071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12524.0,"contact_point_centroid":[0.5651,0.22027,0.14701],"force_p95":0.0957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24326,"mean_force":0.06475,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.55642,0.2364,0.14889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":454.0,"contact_point_centroid":[0.56807,0.22779,0.15669],"force_p95":0.14483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21252,"mean_force":0.05302,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55931,0.24235,0.16022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5161.0,"contact_point_centroid":[0.48843,0.02323,0.02631],"force_p95":0.06737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2052,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48681,0.04206,0.02463]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7284.0,"contact_point_centroid":[0.51948,0.16045,0.12972],"force_p95":0.11321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17275,"mean_force":0.07666,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51959,0.14125,0.12744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9799.0,"contact_point_centroid":[0.52217,0.11494,0.12604],"force_p95":0.09759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16539,"mean_force":0.06013,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51615,0.13252,0.12652]},{"body_a":"world","body_b":"grasp_target","contact_count":3272.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.02103,0.16803]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49548,0.0425,0.03617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.48771,0.06157,0.02755],"force_p95":0.09535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10931,"mean_force":0.05831,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48683,0.04206,0.02465]}],"total_contact_groups":15},"final_pose_error":0.01015,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5686,0.24578,0.01629],"final_tcp_position":[0.56024,0.24269,0.16204],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.58842,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3272.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49632,0.04236,0.0382],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49537,0.04277,0.03364],"tcp_start":[0.49632,0.04236,0.0382],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50138,0.04284,0.02501],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24416,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19449,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11044.0,"raw_peak_contact_force":0.28544,"subtask_id":"grasp_1","tcp_end":[0.48679,0.04206,0.02461],"tcp_start":[0.49537,0.04277,0.03364],"tcp_to_object_dist_end":0.01462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.49704,0.04269,0.11233],"object_pos_start":[0.50138,0.04284,0.02501],"object_to_goal_dist_end":0.21587,"object_to_goal_dist_start":0.24416,"object_z_max":0.11222,"peak_contact_force":0.11786,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22594.0,"raw_peak_contact_force":0.78413,"tcp_end":[0.48265,0.0417,0.12019],"tcp_start":[0.48679,0.04206,0.02461],"tcp_to_object_dist_end":0.01643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.56743,0.23455,0.12476],"object_pos_start":[0.49704,0.04269,0.11233],"object_to_goal_dist_end":0.0245,"object_to_goal_dist_start":0.21587,"object_z_max":0.12473,"peak_contact_force":0.11175,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17083.0,"raw_peak_contact_force":0.17275,"subtask_id":"transport_arc","tcp_end":[0.55484,0.22914,0.13744],"tcp_start":[0.48265,0.0417,0.12019],"tcp_to_object_dist_end":0.01867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.56664,0.246,0.13985],"object_pos_start":[0.56743,0.23455,0.12476],"object_to_goal_dist_end":0.00736,"object_to_goal_dist_start":0.0245,"object_z_max":0.13985,"peak_contact_force":0.15887,"phase_name":"descend_release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21513.0,"raw_peak_contact_force":0.40928,"subtask_id":"release_1","tcp_end":[0.56024,0.24269,0.16204],"tcp_start":[0.55484,0.22914,0.13744],"tcp_to_object_dist_end":0.02333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5686,0.24578,0.01629],"object_pos_start":[0.56664,0.246,0.13985],"object_to_goal_dist_end":0.13056,"object_to_goal_dist_start":0.00736,"object_z_max":0.13985,"peak_contact_force":0.12825,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":975.0,"raw_peak_contact_force":1.58842,"tcp_end":[0.55477,0.24034,0.18372],"tcp_start":[0.56024,0.24269,0.16204],"tcp_to_object_dist_end":0.16809,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58192,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14803,"descend_1.descend_speed":0.07518,"descend_release_1.release_height_offset":0.01754,"descend_release_1.release_speed":0.0634,"lift_1.lift_height":0.14283,"release_1.release_duration":0.21205,"transport_1.transport_speed":0.29089,"transport_1.transport_tolerance":0.01892},"optimized_scores":{"best_composite_score":0.09448,"best_fitness_score":0.64448,"best_task_score":0.33058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.61627,0.15304,-0.00706],"force_p95":1.01467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58681,"mean_force":0.3257,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62208,0.15643,0.20969]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.47259,-0.01824,-0.00115],"force_p95":0.46572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74811,"mean_force":0.10264,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46157,-0.01909,0.02839]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13942.0,"contact_point_centroid":[0.45924,-0.03823,0.09367],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29883,"mean_force":0.05865,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45899,-0.01904,0.09107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16854.0,"contact_point_centroid":[0.46054,-8e-05,0.09174],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29597,"mean_force":0.05001,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45898,-0.01904,0.09007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16940.0,"contact_point_centroid":[0.61858,0.17266,0.19119],"force_p95":0.06936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25457,"mean_force":0.04751,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.62269,0.15414,0.18804]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02009,-0.00209],"force_p95":0.15001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21323,"mean_force":0.12946,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46427,-0.01914,0.02763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16988.0,"contact_point_centroid":[0.62665,0.13533,0.18881],"force_p95":0.0708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20548,"mean_force":0.04856,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.6227,0.15415,0.18806]},{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48527,-0.00944,0.16865]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14909.0,"contact_point_centroid":[0.54325,0.04922,0.16886],"force_p95":0.07618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13116,"mean_force":0.05118,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54076,0.06823,0.16747]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1329.0,"contact_point_centroid":[0.62194,0.17612,0.19847],"force_p95":0.06448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12915,"mean_force":0.03805,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62583,0.1575,0.19454]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.46428,-5e-05,0.028],"force_p95":0.06523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12739,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46306,-0.01912,0.02645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14677.0,"contact_point_centroid":[0.54046,0.08839,0.17016],"force_p95":0.078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12674,"mean_force":0.05125,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54194,0.06947,0.16764]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47169,-0.01911,0.03714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1345.0,"contact_point_centroid":[0.63036,0.13863,0.19599],"force_p95":0.06582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08816,"mean_force":0.03874,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62581,0.15749,0.1945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4448.0,"contact_point_centroid":[0.46267,-0.03839,0.0292],"force_p95":0.07653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08769,"mean_force":0.04923,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46307,-0.01912,0.02646]}],"total_contact_groups":15},"final_pose_error":0.01059,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61659,0.15389,0.02473],"final_tcp_position":[0.6273,0.15786,0.1979],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4726,-0.01903,0.03905],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47143,-0.01923,0.03472],"tcp_start":[0.4726,-0.01903,0.03905],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01948,0.02569],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28821,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14862,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11285.0,"raw_peak_contact_force":0.21323,"subtask_id":"grasp_1","tcp_end":[0.46303,-0.01912,0.02642],"tcp_start":[0.47143,-0.01923,0.03472],"tcp_to_object_dist_end":0.01304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.47106,-0.01955,0.14815],"object_pos_start":[0.47605,-0.01948,0.02569],"object_to_goal_dist_end":0.24375,"object_to_goal_dist_start":0.28821,"object_z_max":0.14804,"peak_contact_force":0.08088,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30930.0,"raw_peak_contact_force":0.74811,"tcp_end":[0.45929,-0.01904,0.15773],"tcp_start":[0.46303,-0.01912,0.02642],"tcp_to_object_dist_end":0.01519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.61616,0.14937,0.16594],"object_pos_start":[0.47106,-0.01955,0.14815],"object_to_goal_dist_end":0.03015,"object_to_goal_dist_start":0.24375,"object_z_max":0.16592,"peak_contact_force":0.07117,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29586.0,"raw_peak_contact_force":0.13116,"subtask_id":"transport_arc","tcp_end":[0.61906,0.14922,0.1801],"tcp_start":[0.45929,-0.01904,0.15773],"tcp_to_object_dist_end":0.01446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.62541,0.15844,0.18006],"object_pos_start":[0.61616,0.14937,0.16594],"object_to_goal_dist_end":0.01165,"object_to_goal_dist_start":0.03015,"object_z_max":0.18006,"peak_contact_force":0.06626,"phase_name":"descend_release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33928.0,"raw_peak_contact_force":0.25457,"subtask_id":"release_1","tcp_end":[0.6273,0.15786,0.1979],"tcp_start":[0.61906,0.14922,0.1801],"tcp_to_object_dist_end":0.01794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61659,0.15389,0.02473],"object_pos_start":[0.62541,0.15844,0.18006],"object_to_goal_dist_end":0.16603,"object_to_goal_dist_start":0.01165,"object_z_max":0.18006,"peak_contact_force":0.07279,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2895.0,"raw_peak_contact_force":1.58681,"tcp_end":[0.62203,0.15642,0.21807],"tcp_start":[0.6273,0.15786,0.1979],"tcp_to_object_dist_end":0.19343,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61579,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11241,"descend_1.descend_speed":0.03585,"descend_release_1.release_height_offset":0.0343,"descend_release_1.release_speed":0.06576,"lift_1.lift_height":0.1468,"release_1.release_duration":0.36762,"transport_1.transport_speed":0.19404,"transport_1.transport_tolerance":0.01709},"optimized_scores":{"best_composite_score":0.20924,"best_fitness_score":0.75924,"best_task_score":0.55737},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":303.0,"contact_point_centroid":[0.62571,0.2059,-0.00421],"force_p95":0.96739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09612,"mean_force":0.24,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61931,0.20435,0.14671]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.45512,-0.02372,-0.00122],"force_p95":0.454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6655,"mean_force":0.10204,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44504,-0.02484,0.02933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14930.0,"contact_point_centroid":[0.44208,-0.04394,0.09684],"force_p95":0.07893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29555,"mean_force":0.05677,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44251,-0.02476,0.0941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17967.0,"contact_point_centroid":[0.4439,-0.00577,0.09542],"force_p95":0.07291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28592,"mean_force":0.04845,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44252,-0.02476,0.09371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17620.0,"contact_point_centroid":[0.61681,0.22094,0.12717],"force_p95":0.0744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25296,"mean_force":0.04947,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.62103,0.20254,0.12292]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45863,-0.02623,-0.00213],"force_p95":0.16192,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23493,"mean_force":0.13282,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44769,-0.02491,0.02843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19559.0,"contact_point_centroid":[0.62595,0.18389,0.12238],"force_p95":0.06911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22961,"mean_force":0.04701,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.62089,0.20241,0.12242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5254.0,"contact_point_centroid":[0.44738,-0.0058,0.0287],"force_p95":0.06486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15817,"mean_force":0.04129,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44651,-0.02488,0.02732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.61996,0.22449,0.13894],"force_p95":0.06536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14259,"mean_force":0.03821,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62376,0.2059,0.13462]},{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47705,-0.01231,0.16881]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19374.0,"contact_point_centroid":[0.52973,0.10864,0.13525],"force_p95":0.07226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13744,"mean_force":0.05018,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53185,0.08986,0.13261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18967.0,"contact_point_centroid":[0.53637,0.07297,0.13328],"force_p95":0.07691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13249,"mean_force":0.05192,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53348,0.09192,0.13211]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45509,-0.02492,0.03753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4487.0,"contact_point_centroid":[0.44581,-0.04418,0.03007],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08557,"mean_force":0.04917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44651,-0.02488,0.02733]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1362.0,"contact_point_centroid":[0.62915,0.18733,0.13426],"force_p95":0.0664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08066,"mean_force":0.03918,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6237,0.20589,0.13452]}],"total_contact_groups":15},"final_pose_error":0.01155,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62475,0.20567,0.02664],"final_tcp_position":[0.62544,0.20643,0.13801],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.09612,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45607,-0.02482,0.0394],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45472,-0.02507,0.03511],"tcp_start":[0.45607,-0.02482,0.0394],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02533,0.02553],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30307,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15922,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11541.0,"raw_peak_contact_force":0.23493,"subtask_id":"grasp_1","tcp_end":[0.44648,-0.02488,0.02729],"tcp_start":[0.45472,-0.02507,0.03511],"tcp_to_object_dist_end":0.01215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.45357,-0.02547,0.15277],"object_pos_start":[0.45849,-0.02533,0.02553],"object_to_goal_dist_end":0.29542,"object_to_goal_dist_start":0.30307,"object_z_max":0.15266,"peak_contact_force":0.08017,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33031.0,"raw_peak_contact_force":0.6655,"tcp_end":[0.44283,-0.02475,0.16288],"tcp_start":[0.44648,-0.02488,0.02729],"tcp_to_object_dist_end":0.01476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.60717,0.19627,0.09103],"object_pos_start":[0.45357,-0.02547,0.15277],"object_to_goal_dist_end":0.03468,"object_to_goal_dist_start":0.29542,"object_z_max":0.1528,"peak_contact_force":0.07727,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38341.0,"raw_peak_contact_force":0.13744,"subtask_id":"transport_arc","tcp_end":[0.61849,0.19785,0.1075],"tcp_start":[0.44283,-0.02475,0.16288],"tcp_to_object_dist_end":0.02005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.62073,0.20719,0.11484],"object_pos_start":[0.60717,0.19627,0.09103],"object_to_goal_dist_end":0.00948,"object_to_goal_dist_start":0.03468,"object_z_max":0.11483,"peak_contact_force":0.06807,"phase_name":"descend_release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":37179.0,"raw_peak_contact_force":0.25296,"subtask_id":"release_1","tcp_end":[0.62544,0.20643,0.13801],"tcp_start":[0.61849,0.19785,0.1075],"tcp_to_object_dist_end":0.02366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62475,0.20567,0.02664],"object_pos_start":[0.62073,0.20719,0.11484],"object_to_goal_dist_end":0.08768,"object_to_goal_dist_start":0.00948,"object_z_max":0.11484,"peak_contact_force":0.13568,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2985.0,"raw_peak_contact_force":1.09612,"tcp_end":[0.61921,0.20432,0.15791],"tcp_start":[0.62544,0.20643,0.13801],"tcp_to_object_dist_end":0.13139,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```