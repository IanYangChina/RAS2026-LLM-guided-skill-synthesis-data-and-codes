## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1891 | 0.42 | ✅ accepted |
| 4 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | force_threshold_switch | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.0704 | 0.16 | ❌ rejected |
| 2 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |
| 1 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0465 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.189) — your mutation base

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
  generator: arc_cartesian
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
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: scale
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
  parameters:
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
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (scale)
- **descend_release_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_speed: status=consumed; consumers=generator.speed (scale)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.189
- **task_score** (E): 0.420
- **fitness_score**: 0.689  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2654 |
| descend_1 | 1.00 | 1.00 | 0.0046 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1231 |
| transport_1 | 0.00 | 1.00 | 0.1215 |
| descend_release_1 | 0.67 | 1.00 | 0.1533 |
| release_1 | 1.00 | 1.00 | 0.0221 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.475, -0.000, 0.039) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.475, -0.000, 0.039)→(0.474, -0.001, 0.034) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.034)→(0.465, -0.001, 0.026) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.278 | 1.00 / 42.667 | 0.167 | 0.245 |
| lift_1 | lift | 1.00 / step_budget | (0.465, -0.001, 0.026)→(0.462, -0.001, 0.149) | (0.479, -0.001, 0.025)→(0.474, -0.001, 0.139) | 0.278→0.250 | 1.00 / 36.000 | 0.093 | 0.737 |
| transport_1 | approach | 0.00 / step_budget | (0.462, -0.001, 0.149)→(0.510, 0.071, 0.223) | (0.474, -0.001, 0.139)→(0.517, 0.072, 0.205) | 0.250→0.171 | 1.00 / 32.667 | 0.103 | 0.189 |
| descend_release_1 | descend | 0.67 / step_budget | (0.510, 0.071, 0.223)→(0.587, 0.182, 0.154) | (0.517, 0.072, 0.205)→(0.582, 0.182, 0.128) | 0.171→0.046 | 1.00 / 36.667 | 0.100 | 0.220 |
| release_1 | release | 1.00 / step_budget | (0.587, 0.182, 0.154)→(0.581, 0.180, 0.175) | (0.582, 0.182, 0.128)→(0.575, 0.183, 0.027) | 0.046→0.132 | 1.00 / 1.667 | 0.266 | 1.432 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.494
- phase_score: 0.315
- phase_breakdown.approach_1_score: 0.821
- phase_breakdown.descend_1_score: 0.735
- phase_breakdown.transport_arc_score: 0.023
- phase_breakdown.release_1_score: 0.255
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.727

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.727
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.494
- **Median Q (composite search score)**: 0.201
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65161,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11634,"descend_1.descend_speed":0.06064,"descend_release_1.release_speed":0.07274,"lift_1.lift_height":0.12032,"release_1.release_duration":0.29049,"transport_1.arc_height":0.08462,"transport_1.transport_speed":0.1544},"optimized_scores":{"best_composite_score":0.20063,"best_fitness_score":0.70063,"best_task_score":0.44771},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.54309,0.24459,-0.00686],"force_p95":1.18917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32792,"mean_force":0.41564,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55271,0.23658,0.15055]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.49753,0.04069,-0.00141],"force_p95":0.47906,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78243,"mean_force":0.10904,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48508,0.0419,0.02683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11595.0,"contact_point_centroid":[0.48363,0.06092,0.08162],"force_p95":0.10891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42677,"mean_force":0.0625,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48257,0.04168,0.07908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":730.0,"contact_point_centroid":[0.55382,0.25764,0.13709],"force_p95":0.14594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33366,"mean_force":0.08046,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55659,0.23831,0.13797]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14272.0,"contact_point_centroid":[0.48494,0.02312,0.07817],"force_p95":0.08994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31877,"mean_force":0.05058,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48259,0.04169,0.07679]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50141,0.04479,-0.00229],"force_p95":0.2039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28544,"mean_force":0.14424,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48805,0.04217,0.02593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1046.0,"contact_point_centroid":[0.5638,0.22179,0.13593],"force_p95":0.11907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24966,"mean_force":0.05112,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55674,0.23837,0.13818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12614.0,"contact_point_centroid":[0.54246,0.16682,0.16887],"force_p95":0.11999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23688,"mean_force":0.06914,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.53525,0.18329,0.17083]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9546.0,"contact_point_centroid":[0.53331,0.20077,0.17047],"force_p95":0.15446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2156,"mean_force":0.09373,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.53451,0.18155,0.17173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5161.0,"contact_point_centroid":[0.48843,0.02323,0.02631],"force_p95":0.06737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2052,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48681,0.04206,0.02463]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12228.0,"contact_point_centroid":[0.49212,0.08896,0.17864],"force_p95":0.11932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20186,"mean_force":0.08004,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49071,0.06966,0.17818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16706.0,"contact_point_centroid":[0.49514,0.051,0.17719],"force_p95":0.0914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18694,"mean_force":0.05805,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49042,0.06892,0.17721]},{"body_a":"world","body_b":"grasp_target","contact_count":3272.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.02103,0.16803]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49548,0.0425,0.03617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.48771,0.06157,0.02755],"force_p95":0.09535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10931,"mean_force":0.05831,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48683,0.04206,0.02465]}],"total_contact_groups":15},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55406,0.24128,0.02673],"final_tcp_position":[0.55851,0.23892,0.14136],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.32792,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3272.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49632,0.04236,0.0382],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49537,0.04277,0.03364],"tcp_start":[0.49632,0.04236,0.0382],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50138,0.04284,0.02501],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24416,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19449,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11044.0,"raw_peak_contact_force":0.28544,"subtask_id":"grasp_1","tcp_end":[0.48679,0.04206,0.02461],"tcp_start":[0.49537,0.04277,0.03364],"tcp_to_object_dist_end":0.01462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.49672,0.04265,0.12462],"object_pos_start":[0.50138,0.04284,0.02501],"object_to_goal_dist_end":0.2144,"object_to_goal_dist_start":0.24416,"object_z_max":0.12451,"peak_contact_force":0.11811,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26023.0,"raw_peak_contact_force":0.78243,"tcp_end":[0.48276,0.04171,0.13317],"tcp_start":[0.48679,0.04206,0.02461],"tcp_to_object_dist_end":0.01639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51761,0.11502,0.1946],"object_pos_start":[0.49672,0.04265,0.12462],"object_to_goal_dist_end":0.14607,"object_to_goal_dist_start":0.2144,"object_z_max":0.19458,"peak_contact_force":0.14448,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28934.0,"raw_peak_contact_force":0.20186,"subtask_id":"transport_arc","tcp_end":[0.5084,0.11312,0.21329],"tcp_start":[0.48276,0.04171,0.13317],"tcp_to_object_dist_end":0.02092,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.55752,0.2393,0.11194],"object_pos_start":[0.51761,0.11502,0.1946],"object_to_goal_dist_end":0.03595,"object_to_goal_dist_start":0.14607,"object_z_max":0.1946,"peak_contact_force":0.14445,"phase_name":"descend_release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22160.0,"raw_peak_contact_force":0.23688,"subtask_id":"release_1","tcp_end":[0.55851,0.23892,0.14136],"tcp_start":[0.5084,0.11312,0.21329],"tcp_to_object_dist_end":0.02945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55406,0.24128,0.02673],"object_pos_start":[0.55752,0.2393,0.11194],"object_to_goal_dist_end":0.12054,"object_to_goal_dist_start":0.03595,"object_z_max":0.11194,"peak_contact_force":0.36774,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1941.0,"raw_peak_contact_force":1.32792,"tcp_end":[0.55259,0.23654,0.16303],"tcp_start":[0.55851,0.23892,0.14136],"tcp_to_object_dist_end":0.13639,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78788,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13357,"descend_1.descend_speed":0.09713,"descend_release_1.release_speed":0.04586,"lift_1.lift_height":0.14946,"release_1.release_duration":0.25152,"transport_1.arc_height":0.13099,"transport_1.transport_speed":0.0644},"optimized_scores":{"best_composite_score":0.13922,"best_fitness_score":0.63922,"best_task_score":0.32006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.59069,0.12448,-0.00861],"force_p95":1.29135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72941,"mean_force":0.49583,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.603,0.13743,0.20607]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.47269,-0.01835,-0.00116],"force_p95":0.47266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75481,"mean_force":0.10366,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46159,-0.0191,0.02836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14527.0,"contact_point_centroid":[0.45932,-0.03823,0.09721],"force_p95":0.08027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29952,"mean_force":0.05842,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45901,-0.01904,0.09465]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17364.0,"contact_point_centroid":[0.46061,-8e-05,0.09469],"force_p95":0.07484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29656,"mean_force":0.05029,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.459,-0.01904,0.09304]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20278.0,"contact_point_centroid":[0.56597,0.07326,0.2282],"force_p95":0.08112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25388,"mean_force":0.05048,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.56283,0.0922,0.2272]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1087.0,"contact_point_centroid":[0.60126,0.15675,0.19421],"force_p95":0.07664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24916,"mean_force":0.04821,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60679,0.13843,0.19171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1421.0,"contact_point_centroid":[0.60836,0.11909,0.19203],"force_p95":0.07486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21514,"mean_force":0.04262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60664,0.13839,0.19142]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02009,-0.00209],"force_p95":0.15001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21323,"mean_force":0.12946,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46427,-0.01914,0.02763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14485.0,"contact_point_centroid":[0.47501,-0.02176,0.22573],"force_p95":0.10216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2111,"mean_force":0.06994,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47192,-0.00292,0.22465]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19426.0,"contact_point_centroid":[0.55884,0.109,0.2308],"force_p95":0.07615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20164,"mean_force":0.05147,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.5608,0.09011,0.22868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15028.0,"contact_point_centroid":[0.47535,0.01555,0.22472],"force_p95":0.09464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17799,"mean_force":0.0659,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47169,-0.00315,0.22398]},{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48527,-0.00944,0.16865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.46428,-5e-05,0.028],"force_p95":0.06523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12739,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46306,-0.01912,0.02645]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47169,-0.01911,0.03714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4448.0,"contact_point_centroid":[0.46267,-0.03839,0.0292],"force_p95":0.07653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08769,"mean_force":0.04923,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46307,-0.01912,0.02646]}],"total_contact_groups":15},"final_pose_error":0.0313,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.59712,0.12988,0.02519],"final_tcp_position":[0.60834,0.13864,0.19499],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4726,-0.01903,0.03905],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47143,-0.01923,0.03472],"tcp_start":[0.4726,-0.01903,0.03905],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01948,0.02569],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28821,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14862,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11285.0,"raw_peak_contact_force":0.21323,"subtask_id":"grasp_1","tcp_end":[0.46303,-0.01912,0.02642],"tcp_start":[0.47143,-0.01923,0.03472],"tcp_to_object_dist_end":0.01304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.47109,-0.01953,0.15419],"object_pos_start":[0.47605,-0.01948,0.02569],"object_to_goal_dist_end":0.24276,"object_to_goal_dist_start":0.28821,"object_z_max":0.15407,"peak_contact_force":0.08095,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32022.0,"raw_peak_contact_force":0.75481,"tcp_end":[0.45935,-0.01904,0.16428],"tcp_start":[0.46303,-0.01912,0.02642],"tcp_to_object_dist_end":0.01549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,0.02987,0.25733],"object_pos_start":[0.47109,-0.01953,0.15419],"object_to_goal_dist_end":0.18739,"object_to_goal_dist_start":0.24276,"object_z_max":0.25726,"peak_contact_force":0.09876,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29513.0,"raw_peak_contact_force":0.2111,"subtask_id":"transport_arc","tcp_end":[0.50369,0.02952,0.27579],"tcp_start":[0.45935,-0.01904,0.16428],"tcp_to_object_dist_end":0.02101,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60198,0.13869,0.16952],"object_pos_start":[0.5137,0.02987,0.25733],"object_to_goal_dist_end":0.04132,"object_to_goal_dist_start":0.18739,"object_z_max":0.25733,"peak_contact_force":0.07325,"phase_name":"descend_release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":39704.0,"raw_peak_contact_force":0.25388,"subtask_id":"release_1","tcp_end":[0.60834,0.13864,0.19499],"tcp_start":[0.50369,0.02952,0.27579],"tcp_to_object_dist_end":0.02625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59712,0.12988,0.02519],"object_pos_start":[0.60198,0.13869,0.16952],"object_to_goal_dist_end":0.17089,"object_to_goal_dist_start":0.04132,"object_z_max":0.16952,"peak_contact_force":0.2329,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2657.0,"raw_peak_contact_force":1.72941,"tcp_end":[0.60294,0.13742,0.21578],"tcp_start":[0.60834,0.13864,0.19499],"tcp_to_object_dist_end":0.19083,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6646,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16418,"descend_1.descend_speed":0.04961,"descend_release_1.release_speed":0.03336,"lift_1.lift_height":0.13399,"release_1.release_duration":0.28489,"transport_1.arc_height":0.05251,"transport_1.transport_speed":0.17915},"optimized_scores":{"best_composite_score":0.22733,"best_fitness_score":0.72733,"best_task_score":0.49356},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.57762,0.17243,-0.00706],"force_p95":0.9718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23995,"mean_force":0.41139,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58702,0.16625,0.13404]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.4551,-0.02372,-0.00119],"force_p95":0.45718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67253,"mean_force":0.10014,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44503,-0.02484,0.02937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12947.0,"contact_point_centroid":[0.44265,-0.04396,0.09006],"force_p95":0.08007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29994,"mean_force":0.05874,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44248,-0.02476,0.08745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15771.0,"contact_point_centroid":[0.44425,-0.00581,0.0884],"force_p95":0.07553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28966,"mean_force":0.04969,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44248,-0.02476,0.08685]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45863,-0.02623,-0.00213],"force_p95":0.16192,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23493,"mean_force":0.13282,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44769,-0.02491,0.02843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.58716,0.18642,0.12352],"force_p95":0.09062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21399,"mean_force":0.05659,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59132,0.16753,0.1214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21757.0,"contact_point_centroid":[0.56183,0.10634,0.14794],"force_p95":0.06889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16945,"mean_force":0.04639,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.55823,0.12523,0.14679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1225.0,"contact_point_centroid":[0.59521,0.14886,0.12177],"force_p95":0.07047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16648,"mean_force":0.04128,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59163,0.16762,0.12187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20227.0,"contact_point_centroid":[0.55368,0.14239,0.1507],"force_p95":0.07273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16644,"mean_force":0.04873,"phase_index":5.0,"phase_name":"descend_release_1","phase_type":"descend","tcp_position_centroid":[0.55691,0.12362,0.14764]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5254.0,"contact_point_centroid":[0.44738,-0.0058,0.0287],"force_p95":0.06486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15817,"mean_force":0.04129,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44651,-0.02488,0.02732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17150.0,"contact_point_centroid":[0.48153,0.00559,0.17085],"force_p95":0.08902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15508,"mean_force":0.05888,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47905,0.0246,0.16934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18998.0,"contact_point_centroid":[0.47879,0.04216,0.17001],"force_p95":0.08011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14155,"mean_force":0.05254,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47795,0.02323,0.1689]},{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47705,-0.01231,0.16881]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45509,-0.02492,0.03753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4487.0,"contact_point_centroid":[0.44581,-0.04418,0.03007],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08557,"mean_force":0.04917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44651,-0.02488,0.02733]}],"total_contact_groups":15},"final_pose_error":0.05554,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.57523,0.17691,0.02912],"final_tcp_position":[0.59338,0.16799,0.12493],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.23995,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45607,-0.02482,0.0394],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45472,-0.02507,0.03511],"tcp_start":[0.45607,-0.02482,0.0394],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02533,0.02553],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30307,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15922,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11541.0,"raw_peak_contact_force":0.23493,"subtask_id":"grasp_1","tcp_end":[0.44648,-0.02488,0.02729],"tcp_start":[0.45472,-0.02507,0.03511],"tcp_to_object_dist_end":0.01215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.45482,-0.02552,0.13921],"object_pos_start":[0.45849,-0.02533,0.02553],"object_to_goal_dist_end":0.29325,"object_to_goal_dist_start":0.30307,"object_z_max":0.13909,"peak_contact_force":0.07991,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28852.0,"raw_peak_contact_force":0.67253,"tcp_end":[0.44273,-0.02475,0.15],"tcp_start":[0.44648,-0.02488,0.02729],"tcp_to_object_dist_end":0.01622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52096,0.07222,0.16235],"object_pos_start":[0.45482,-0.02552,0.13921],"object_to_goal_dist_end":0.18094,"object_to_goal_dist_start":0.29325,"object_z_max":0.16245,"peak_contact_force":0.06668,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36148.0,"raw_peak_contact_force":0.15508,"subtask_id":"transport_arc","tcp_end":[0.5167,0.07123,0.17976],"tcp_start":[0.44273,-0.02475,0.15],"tcp_to_object_dist_end":0.01795,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58736,0.16811,0.10216],"object_pos_start":[0.52096,0.07222,0.16235],"object_to_goal_dist_end":0.05983,"object_to_goal_dist_start":0.18094,"object_z_max":0.16235,"peak_contact_force":0.08176,"phase_name":"descend_release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":41984.0,"raw_peak_contact_force":0.16945,"subtask_id":"release_1","tcp_end":[0.59338,0.16799,0.12493],"tcp_start":[0.5167,0.07123,0.17976],"tcp_to_object_dist_end":0.02355,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57523,0.17691,0.02912],"object_pos_start":[0.58736,0.16811,0.10216],"object_to_goal_dist_end":0.10592,"object_to_goal_dist_start":0.05983,"object_z_max":0.10216,"peak_contact_force":0.19676,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2517.0,"raw_peak_contact_force":1.23995,"tcp_end":[0.58689,0.16622,0.14618],"tcp_start":[0.59338,0.16799,0.12493],"tcp_to_object_dist_end":0.11813,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```