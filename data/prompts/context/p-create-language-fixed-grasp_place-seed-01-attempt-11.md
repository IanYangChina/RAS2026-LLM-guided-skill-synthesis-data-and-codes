## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3655 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2498 | 0.17 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3067 | 0.29 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | time_limit | 3 | 0.2626 | 0.20 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2555 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.366) — your mutation base

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
    - 0.08
    orientation:
      mode: keep_current
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
    - 0.02
    orientation:
      mode: keep_current
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
  subtask_id: grasp_1
- id: lift_1
  type: lift
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_to_goal
  type: approach
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
    - 0.12
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_goal
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
    orientation:
      mode: keep_current
  subtask_id: transport_arc
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.12]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.366
- **task_score** (E): 0.306
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1863 |
| descend_1 | 1.00 | 1.00 | 0.0645 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 1.00 | 1.00 | 0.1030 |
| transport_to_goal | 1.00 | 1.00 | 0.2394 |
| descend_to_goal | 1.00 | 1.00 | 0.0953 |
| release_1 | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.146 | 0.197 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.047)→(0.474, -0.001, 0.149) | (0.479, -0.001, 0.026)→(0.485, -0.001, 0.122) | 0.278→0.247 | 1.00 / 25.333 | 0.097 | 0.389 |
| transport_to_goal | approach | 1.00 / step_budget | (0.474, -0.001, 0.149)→(0.589, 0.178, 0.247) | (0.485, -0.001, 0.122)→(0.550, 0.106, 0.016) | 0.247→0.180 | 1.00 / 8.667 | 182006.988 | 1.629 |
| descend_to_goal | descend | 1.00 / step_budget | (0.589, 0.178, 0.247)→(0.602, 0.199, 0.155) | (0.550, 0.106, 0.016)→(0.550, 0.106, 0.016) | 0.180→0.180 | 1.00 / 8.000 | 3249.700 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.199, 0.155)→(0.596, 0.197, 0.175) | (0.550, 0.106, 0.016)→(0.550, 0.106, 0.016) | 0.180→0.180 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.366
- phase_score: 0.783
- phase_breakdown.release_1_score: 0.572
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.877
- phase_breakdown.transport_arc_score: 0.820
- phase_breakdown.approach_1_score: 0.167
- grasp_place_fitness: 0.645

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.645
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.366
- **Median Q (composite search score)**: 0.368
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.125


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01587,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.13437,"transport_to_goal.transport_speed":0.425},"optimized_scores":{"best_composite_score":0.36806,"best_fitness_score":0.61806,"best_task_score":0.3102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2465.0,"contact_point_centroid":[0.54048,0.1287,-0.00244],"force_p95":0.21817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5968,"mean_force":0.1481,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53503,0.16604,0.21406]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.49948,0.04252,-0.00124],"force_p95":0.25116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40985,"mean_force":0.0524,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48696,0.04314,0.04763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10589.0,"contact_point_centroid":[0.49234,0.06202,0.09047],"force_p95":0.10124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28199,"mean_force":0.06246,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48964,0.04313,0.08896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9618.0,"contact_point_centroid":[0.49213,0.0242,0.09144],"force_p95":0.10691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26193,"mean_force":0.06677,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48979,0.04313,0.09039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2665.0,"contact_point_centroid":[0.507,0.04629,0.15664],"force_p95":0.14746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24741,"mean_force":0.09052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50103,0.06494,0.15638]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22302,"mean_force":0.1335,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48927,0.04337,0.04693]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.50796,0.0858,0.1578],"force_p95":0.10162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18033,"mean_force":0.07453,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50177,0.06746,0.15768]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.48842,0.02404,0.0475],"force_p95":0.07795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13945,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.0457]},{"body_a":"world","body_b":"grasp_target","contact_count":2296.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49758,0.0204,0.20872]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49548,0.04263,0.08617]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.54094,0.13006,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55577,0.22954,0.19941]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54094,0.13006,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55488,0.23786,0.1542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5271.0,"contact_point_centroid":[0.48881,0.06245,0.04779],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07405,"mean_force":0.04219,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.04571]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2553.0,"contact_point_centroid":[0.53628,0.16841,0.21772],"force_p95":0.01136,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53584,0.1684,0.21543]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1168.0,"contact_point_centroid":[0.55618,0.22957,0.20163],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55577,0.22954,0.19941]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.55802,0.23915,0.15233],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55749,0.23911,0.1499]}],"total_contact_groups":16},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54094,0.13006,0.01602],"final_tcp_position":[0.55924,0.23972,0.15332],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273011.26743,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49718,0.04149,0.11825],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":832.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49602,0.04398,0.05434],"tcp_start":[0.49718,0.04149,0.11825],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16032,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11401.0,"raw_peak_contact_force":0.22302,"subtask_id":"grasp_1","tcp_end":[0.48811,0.04327,0.04567],"tcp_start":[0.49602,0.04398,0.05434],"tcp_to_object_dist_end":0.02405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":635.0,"n_steps_budget":720.0,"object_pos_end":[0.50795,0.04396,0.12077],"object_pos_start":[0.50115,0.04379,0.02547],"object_to_goal_dist_end":0.21031,"object_to_goal_dist_start":0.24321,"object_z_max":0.12066,"peak_contact_force":0.09953,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20356.0,"raw_peak_contact_force":0.40985,"tcp_end":[0.49649,0.04341,0.14772],"tcp_start":[0.48811,0.04327,0.04567],"tcp_to_object_dist_end":0.02929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54094,0.13006,0.01602],"object_pos_start":[0.50795,0.04396,0.12077],"object_to_goal_dist_end":0.17558,"object_to_goal_dist_start":0.21031,"object_z_max":0.13847,"peak_contact_force":273011.26743,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10935.0,"raw_peak_contact_force":1.5968,"tcp_end":[0.55405,0.22069,0.24574],"tcp_start":[0.49649,0.04341,0.14772],"tcp_to_object_dist_end":0.24729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.54094,0.13006,0.01602],"object_pos_start":[0.54094,0.13006,0.01602],"object_to_goal_dist_end":0.17558,"object_to_goal_dist_start":0.17558,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.55924,0.23972,0.15332],"tcp_start":[0.55405,0.22069,0.24574],"tcp_to_object_dist_end":0.17667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54094,0.13006,0.01602],"object_pos_start":[0.54094,0.13006,0.01602],"object_to_goal_dist_end":0.17558,"object_to_goal_dist_start":0.17558,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55333,0.2371,0.17413],"tcp_start":[0.55924,0.23972,0.15332],"tcp_to_object_dist_end":0.19134,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13934,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.12609,"transport_to_goal.transport_speed":0.32444},"optimized_scores":{"best_composite_score":0.33373,"best_fitness_score":0.58373,"best_task_score":0.24263},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2221.0,"contact_point_centroid":[0.54557,0.07237,-0.00245],"force_p95":0.15617,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73102,"mean_force":0.14676,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56891,0.09199,0.23969]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.47476,-0.01921,-0.0011],"force_p95":0.24427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38022,"mean_force":0.0419,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46282,-0.01953,0.04884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4309.0,"contact_point_centroid":[0.49746,0.02468,0.16002],"force_p95":0.11316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28459,"mean_force":0.07689,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49159,0.00613,0.16051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4060.0,"contact_point_centroid":[0.4961,-0.01419,0.15859],"force_p95":0.14021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27425,"mean_force":0.08143,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49012,0.00446,0.15901]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9457.0,"contact_point_centroid":[0.46749,-0.00054,0.08903],"force_p95":0.10324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26705,"mean_force":0.06508,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46531,-0.01952,0.08813]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10380.0,"contact_point_centroid":[0.46732,-0.03842,0.08882],"force_p95":0.09705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25966,"mean_force":0.05998,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46529,-0.01952,0.08793]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13758,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17752,"mean_force":0.12663,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46499,-0.01959,0.0481]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48633,-0.00907,0.2097]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47183,-0.01908,0.08713]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.54565,0.07262,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61514,0.1442,0.23683]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54565,0.07262,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6203,0.15345,0.19479]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46342,-0.00031,0.04912],"force_p95":0.06792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09914,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01956,0.047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5391.0,"contact_point_centroid":[0.46347,-0.03878,0.04883],"force_p95":0.06505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0819,"mean_force":0.041,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01956,0.047]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2163.0,"contact_point_centroid":[0.57261,0.09572,0.24543],"force_p95":0.01116,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01573,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5723,0.09572,0.24315]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62313,0.15425,0.19362],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62276,0.15423,0.19124]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1097.0,"contact_point_centroid":[0.61537,0.14417,0.23936],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.6151,0.14416,0.23703]}],"total_contact_groups":16},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.54565,0.07262,0.01602],"final_tcp_position":[0.62438,0.15451,0.19506],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273009.57355,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47418,-0.01851,0.11955],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":856.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47153,-0.01974,0.05481],"tcp_start":[0.47418,-0.01851,0.11955],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13643,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.17752,"subtask_id":"grasp_1","tcp_end":[0.46387,-0.01956,0.04697],"tcp_start":[0.47153,-0.01974,0.05481],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.48281,-0.01986,0.11345],"object_pos_start":[0.47609,-0.01971,0.0258],"object_to_goal_dist_end":0.24497,"object_to_goal_dist_start":0.28827,"object_z_max":0.11334,"peak_contact_force":0.09508,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19974.0,"raw_peak_contact_force":0.38022,"tcp_end":[0.47147,-0.01959,0.14056],"tcp_start":[0.46387,-0.01956,0.04697],"tcp_to_object_dist_end":0.02938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54565,0.07262,0.01602],"object_pos_start":[0.48281,-0.01986,0.11345],"object_to_goal_dist_end":0.21243,"object_to_goal_dist_start":0.24497,"object_z_max":0.15139,"peak_contact_force":273009.57355,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12753.0,"raw_peak_contact_force":1.73102,"tcp_end":[0.60805,0.13516,0.27962],"tcp_start":[0.47147,-0.01959,0.14056],"tcp_to_object_dist_end":0.27801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.54565,0.07262,0.01602],"object_pos_start":[0.54565,0.07262,0.01602],"object_to_goal_dist_end":0.21243,"object_to_goal_dist_start":0.21243,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2129.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.62438,0.15451,0.19506],"tcp_start":[0.60805,0.13516,0.27962],"tcp_to_object_dist_end":0.21204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54565,0.07262,0.01602],"object_pos_start":[0.54565,0.07262,0.01602],"object_to_goal_dist_end":0.21243,"object_to_goal_dist_start":0.21243,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61886,0.15299,0.2142],"tcp_start":[0.62438,0.15451,0.19506],"tcp_to_object_dist_end":0.22604,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14729,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.14578,"transport_to_goal.transport_speed":0.40202},"optimized_scores":{"best_composite_score":0.39479,"best_fitness_score":0.64479,"best_task_score":0.36582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1618.0,"contact_point_centroid":[0.56377,0.11459,-0.00263],"force_p95":0.27465,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55938,"mean_force":0.15264,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57399,0.13709,0.20444]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.45693,-0.02481,-0.00113],"force_p95":0.29142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37815,"mean_force":0.03969,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44585,-0.02545,0.04954]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5147.0,"contact_point_centroid":[0.49204,0.00281,0.16852],"force_p95":0.14961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27956,"mean_force":0.0923,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48646,0.02108,0.17039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10757.0,"contact_point_centroid":[0.45046,-0.00646,0.09824],"force_p95":0.10296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27151,"mean_force":0.06548,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44822,-0.02543,0.09762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4944.0,"contact_point_centroid":[0.49271,0.04046,0.1686],"force_p95":0.12689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25345,"mean_force":0.0952,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48726,0.02212,0.17072]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11872.0,"contact_point_centroid":[0.45019,-0.04433,0.09782],"force_p95":0.09666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25313,"mean_force":0.06019,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44818,-0.02543,0.09715]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00207],"force_p95":0.14286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19114,"mean_force":0.12786,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44797,-0.02554,0.04873]},{"body_a":"world","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4784,-0.01185,0.20979]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45518,-0.02493,0.0873]},{"body_a":"world","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.56387,0.11472,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61239,0.18961,0.16559]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56387,0.11472,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61752,0.20122,0.11737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44709,-0.00626,0.04884],"force_p95":0.0727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10424,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44691,-0.0255,0.0477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.44631,-0.04465,0.04879],"force_p95":0.06531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0767,"mean_force":0.04081,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44692,-0.0255,0.04771]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1470.0,"contact_point_centroid":[0.57883,0.14314,0.20847],"force_p95":0.0121,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01698,"mean_force":0.01068,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57858,0.14314,0.20622]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1346.0,"contact_point_centroid":[0.61271,0.18971,0.16749],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61245,0.1897,0.16526]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.62104,0.20242,0.11633],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.00984,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62064,0.2024,0.114]}],"total_contact_groups":16},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.56387,0.11472,0.01602],"final_tcp_position":[0.62261,0.2029,0.11781],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.85482,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45796,-0.02419,0.11958],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45432,-0.02577,0.05497],"tcp_start":[0.45796,-0.02419,0.11958],"tcp_to_object_dist_end":0.02927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.0257,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1411,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.19114,"subtask_id":"grasp_1","tcp_end":[0.44689,-0.0255,0.04768],"tcp_start":[0.45432,-0.02577,0.05497],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.46482,-0.02586,0.13181],"object_pos_start":[0.4585,-0.0257,0.02575],"object_to_goal_dist_end":0.28711,"object_to_goal_dist_start":0.30328,"object_z_max":0.13169,"peak_contact_force":0.09677,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22755.0,"raw_peak_contact_force":0.37815,"tcp_end":[0.45423,-0.02553,0.1602],"tcp_start":[0.44689,-0.0255,0.04768],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56387,0.11472,0.01602],"object_pos_start":[0.46482,-0.02586,0.13181],"object_to_goal_dist_end":0.15084,"object_to_goal_dist_start":0.28711,"object_z_max":0.14969,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13179.0,"raw_peak_contact_force":1.55938,"tcp_end":[0.60467,0.17757,0.21623],"tcp_start":[0.45423,-0.02553,0.1602],"tcp_to_object_dist_end":0.21377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.56387,0.11472,0.01602],"object_pos_start":[0.56387,0.11472,0.01602],"object_to_goal_dist_end":0.15084,"object_to_goal_dist_start":0.15084,"object_z_max":0.01602,"peak_contact_force":9748.85482,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2610.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.62261,0.2029,0.11781],"tcp_start":[0.60467,0.17757,0.21623],"tcp_to_object_dist_end":0.14692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56387,0.11472,0.01602],"object_pos_start":[0.56387,0.11472,0.01602],"object_to_goal_dist_end":0.15084,"object_to_goal_dist_start":0.15084,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61563,0.20051,0.13669],"tcp_start":[0.62261,0.2029,0.11781],"tcp_to_object_dist_end":0.15684,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```