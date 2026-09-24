## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3067 | 0.29 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | time_limit | 3 | 0.2626 | 0.20 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2555 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3705 | 0.32 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3628 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.307) — your mutation base

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

- **Composite score**: 0.307
- **task_score** (E): 0.289
- **fitness_score**: 0.607  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1863 |
| descend_1 | 1.00 | 1.00 | 0.0645 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 1.00 | 1.00 | 0.0990 |
| transport_horizontal | 1.00 | 1.00 | 0.2509 |
| descend_to_goal | 1.00 | 1.00 | 0.0879 |
| release_1 | 1.00 | 1.00 | 0.0204 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.146 | 0.197 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.047)→(0.474, -0.001, 0.145) | (0.479, -0.001, 0.026)→(0.485, -0.001, 0.118) | 0.278→0.246 | 1.00 / 24.667 | 0.099 | 0.389 |
| transport_horizontal | approach | 1.00 / step_budget | (0.474, -0.001, 0.145)→(0.589, 0.177, 0.272) | (0.485, -0.001, 0.118)→(0.536, 0.097, 0.016) | 0.246→0.189 | 1.00 / 8.667 | 94251.511 | 1.585 |
| descend_to_goal | descend | 1.00 / step_budget | (0.589, 0.177, 0.272)→(0.602, 0.199, 0.188) | (0.536, 0.097, 0.016)→(0.536, 0.097, 0.016) | 0.189→0.189 | 1.00 / 8.333 | 3249.658 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.199, 0.188)→(0.597, 0.197, 0.208) | (0.536, 0.097, 0.016)→(0.536, 0.097, 0.016) | 0.189→0.189 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.332
- phase_score: 0.623
- phase_breakdown.release_1_score: 0.388
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.877
- phase_breakdown.transport_arc_score: 0.579
- phase_breakdown.approach_1_score: 0.167
- grasp_place_fitness: 0.628

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.628
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.332
- **Median Q (composite search score)**: 0.322
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.254


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.016,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_to_goal_height":0.02892,"lift_1.lift_height":0.13029,"transport_horizontal.transport_speed":0.37927},"optimized_scores":{"best_composite_score":0.32153,"best_fitness_score":0.62153,"best_task_score":0.31714},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2465.0,"contact_point_centroid":[0.5313,0.1372,-0.00235],"force_p95":0.14317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44171,"mean_force":0.14458,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.53481,0.16494,0.23009]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.49963,0.04267,-0.00124],"force_p95":0.24952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40826,"mean_force":0.05036,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48696,0.04314,0.04765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3430.0,"contact_point_centroid":[0.50798,0.08606,0.15816],"force_p95":0.10961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31389,"mean_force":0.07924,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.50182,0.06775,0.15812]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10535.0,"contact_point_centroid":[0.49236,0.06202,0.0889],"force_p95":0.10118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2811,"mean_force":0.06247,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48964,0.04312,0.08741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9608.0,"contact_point_centroid":[0.49212,0.0242,0.08984],"force_p95":0.10689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26027,"mean_force":0.06653,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48979,0.04313,0.0888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2824.0,"contact_point_centroid":[0.50688,0.04622,0.1563],"force_p95":0.14531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23686,"mean_force":0.08932,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.50094,0.06486,0.15611]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22302,"mean_force":0.1335,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48927,0.04337,0.04693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.48842,0.02404,0.0475],"force_p95":0.07795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13945,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.0457]},{"body_a":"world","body_b":"grasp_target","contact_count":2296.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49758,0.0204,0.20872]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49548,0.04263,0.08617]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.53111,0.13778,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55576,0.22837,0.22645]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53111,0.13778,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55554,0.2377,0.18318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5271.0,"contact_point_centroid":[0.48881,0.06245,0.04779],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07405,"mean_force":0.04219,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.04571]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2471.0,"contact_point_centroid":[0.53623,0.16784,0.23447],"force_p95":0.01114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.53581,0.16782,0.23224]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1127.0,"contact_point_centroid":[0.55621,0.22837,0.22882],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55575,0.22834,0.22659]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.55809,0.23891,0.18115],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5579,0.23887,0.1789]}],"total_contact_groups":16},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.53111,0.13778,0.01602],"final_tcp_position":[0.55953,0.23941,0.18236],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273005.49265,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49718,0.04149,0.11825],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":832.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49602,0.04398,0.05434],"tcp_start":[0.49718,0.04149,0.11825],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16032,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11401.0,"raw_peak_contact_force":0.22302,"subtask_id":"grasp_1","tcp_end":[0.48811,0.04327,0.04567],"tcp_start":[0.49602,0.04398,0.05434],"tcp_to_object_dist_end":0.02405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50784,0.04395,0.11695],"object_pos_start":[0.50115,0.04379,0.02547],"object_to_goal_dist_end":0.21085,"object_to_goal_dist_start":0.24321,"object_z_max":0.11684,"peak_contact_force":0.09626,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20293.0,"raw_peak_contact_force":0.40826,"tcp_end":[0.49645,0.0434,0.14389],"tcp_start":[0.48811,0.04327,0.04567],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53111,0.13778,0.01602],"object_pos_start":[0.50784,0.04395,0.11695],"object_to_goal_dist_end":0.17226,"object_to_goal_dist_start":0.21085,"object_z_max":0.14279,"peak_contact_force":273005.49265,"phase_name":"transport_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11190.0,"raw_peak_contact_force":1.44171,"tcp_end":[0.55361,0.2188,0.27033],"tcp_start":[0.49645,0.0434,0.14389],"tcp_to_object_dist_end":0.26786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.53111,0.13778,0.01602],"object_pos_start":[0.53111,0.13778,0.01602],"object_to_goal_dist_end":0.17226,"object_to_goal_dist_start":0.17226,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2183.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.55953,0.23941,0.18236],"tcp_start":[0.55361,0.2188,0.27033],"tcp_to_object_dist_end":0.19699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53111,0.13778,0.01602],"object_pos_start":[0.53111,0.13778,0.01602],"object_to_goal_dist_end":0.17226,"object_to_goal_dist_start":0.17226,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55414,0.237,0.20309],"tcp_start":[0.55953,0.23941,0.18236],"tcp_to_object_dist_end":0.213,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14634,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_to_goal_height":0.04885,"lift_1.lift_height":0.13815,"transport_horizontal.transport_speed":0.41497},"optimized_scores":{"best_composite_score":0.27074,"best_fitness_score":0.57074,"best_task_score":0.21666},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2726.0,"contact_point_centroid":[0.52757,0.05149,-0.00239],"force_p95":0.13001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77253,"mean_force":0.14096,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.56031,0.08218,0.25276]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.4747,-0.01918,-0.0011],"force_p95":0.25531,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38228,"mean_force":0.04241,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4628,-0.01953,0.04883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2525.0,"contact_point_centroid":[0.48852,-0.0233,0.16377],"force_p95":0.15429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32089,"mean_force":0.08536,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.4824,-0.00467,0.16429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2754.0,"contact_point_centroid":[0.48967,0.01524,0.16492],"force_p95":0.12516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28243,"mean_force":0.07856,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.48359,-0.00327,0.16564]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10229.0,"contact_point_centroid":[0.46776,-0.00056,0.09445],"force_p95":0.1031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26892,"mean_force":0.0659,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46535,-0.01952,0.09357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11176.0,"contact_point_centroid":[0.46754,-0.03841,0.09394],"force_p95":0.09712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26123,"mean_force":0.06099,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46529,-0.01952,0.09306]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13758,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17752,"mean_force":0.12663,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46499,-0.01959,0.0481]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48633,-0.00907,0.2097]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47183,-0.01908,0.08713]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.52762,0.05158,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61544,0.14387,0.2748]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52762,0.05158,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62094,0.15294,0.24284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46342,-0.00031,0.04912],"force_p95":0.06792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09914,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01956,0.047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5391.0,"contact_point_centroid":[0.46347,-0.03878,0.04883],"force_p95":0.06505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0819,"mean_force":0.041,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01956,0.047]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2669.0,"contact_point_centroid":[0.56443,0.08634,0.25937],"force_p95":0.01133,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.56409,0.08634,0.25705]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.62322,0.15364,0.24159],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01028,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62295,0.15363,0.23935]},{"body_a":"left_finger","body_b":"right_finger","contact_count":893.0,"contact_point_centroid":[0.61573,0.1439,0.27713],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61545,0.14389,0.27471]}],"total_contact_groups":16},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52762,0.05158,0.01602],"final_tcp_position":[0.62429,0.15381,0.24314],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.91712,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47418,-0.01851,0.11955],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":856.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47153,-0.01974,0.05481],"tcp_start":[0.47418,-0.01851,0.11955],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13643,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.17752,"subtask_id":"grasp_1","tcp_end":[0.46387,-0.01956,0.04697],"tcp_start":[0.47153,-0.01974,0.05481],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.48268,-0.01985,0.12482],"object_pos_start":[0.47609,-0.01971,0.0258],"object_to_goal_dist_end":0.24172,"object_to_goal_dist_start":0.28827,"object_z_max":0.12471,"peak_contact_force":0.09655,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21538.0,"raw_peak_contact_force":0.38228,"tcp_end":[0.47162,-0.01959,0.15244],"tcp_start":[0.46387,-0.01956,0.04697],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52762,0.05158,0.01602],"object_pos_start":[0.48268,-0.01985,0.12482],"object_to_goal_dist_end":0.22941,"object_to_goal_dist_start":0.24172,"object_z_max":0.15005,"peak_contact_force":9748.91712,"phase_name":"transport_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10674.0,"raw_peak_contact_force":1.77253,"tcp_end":[0.60844,0.13523,0.30722],"tcp_start":[0.47162,-0.01959,0.15244],"tcp_to_object_dist_end":0.31357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.52762,0.05158,0.01602],"object_pos_start":[0.52762,0.05158,0.01602],"object_to_goal_dist_end":0.22941,"object_to_goal_dist_start":0.22941,"object_z_max":0.01602,"peak_contact_force":9748.72917,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1725.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.62429,0.15381,0.24314],"tcp_start":[0.60844,0.13523,0.30722],"tcp_to_object_dist_end":0.26717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52762,0.05158,0.01602],"object_pos_start":[0.52762,0.05158,0.01602],"object_to_goal_dist_end":0.22941,"object_to_goal_dist_start":0.22941,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61982,0.15254,0.26222],"tcp_start":[0.62429,0.15381,0.24314],"tcp_to_object_dist_end":0.28162,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.144,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_to_goal_height":0.02185,"lift_1.lift_height":0.12563,"transport_horizontal.transport_speed":0.38191},"optimized_scores":{"best_composite_score":0.32793,"best_fitness_score":0.62793,"best_task_score":0.3321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1981.0,"contact_point_centroid":[0.54876,0.10261,-0.0025],"force_p95":0.19144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54085,"mean_force":0.14816,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.56629,0.12684,0.21416]},{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.45713,-0.02468,-0.00111],"force_p95":0.27876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37523,"mean_force":0.03758,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44589,-0.02545,0.04958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.48622,-0.00508,0.1559],"force_p95":0.13571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28854,"mean_force":0.08181,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.48035,0.01334,0.15639]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4659.0,"contact_point_centroid":[0.48616,0.03219,0.15553],"force_p95":0.12688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27558,"mean_force":0.08565,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.48059,0.01365,0.15655]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9262.0,"contact_point_centroid":[0.45003,-0.00641,0.08974],"force_p95":0.10278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2691,"mean_force":0.06343,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44824,-0.02543,0.08907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10333.0,"contact_point_centroid":[0.44983,-0.04437,0.08983],"force_p95":0.09513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25105,"mean_force":0.05774,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44825,-0.02543,0.08912]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00207],"force_p95":0.14286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19114,"mean_force":0.12786,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44797,-0.02554,0.04873]},{"body_a":"world","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4784,-0.01185,0.20979]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45518,-0.02493,0.0873]},{"body_a":"world","body_b":"grasp_target","contact_count":1264.0,"contact_point_centroid":[0.54887,0.10279,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61231,0.18917,0.18854]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54887,0.10279,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61803,0.20128,0.13942]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44709,-0.00626,0.04884],"force_p95":0.0727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10424,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44691,-0.0255,0.0477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.44631,-0.04465,0.04879],"force_p95":0.06531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0767,"mean_force":0.04081,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44692,-0.0255,0.04771]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1883.0,"contact_point_centroid":[0.57086,0.13238,0.21927],"force_p95":0.01183,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0155,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_horizontal","phase_type":"approach","tcp_position_centroid":[0.57052,0.13238,0.217]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1352.0,"contact_point_centroid":[0.61271,0.18923,0.1907],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61235,0.18922,0.1884]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.6212,0.20241,0.1382],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62095,0.2024,0.13604]}],"total_contact_groups":16},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.54887,0.10279,0.01602],"final_tcp_position":[0.62282,0.20287,0.1399],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.54085,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45796,-0.02419,0.11958],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45432,-0.02577,0.05497],"tcp_start":[0.45796,-0.02419,0.11958],"tcp_to_object_dist_end":0.02927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.0257,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1411,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.19114,"subtask_id":"grasp_1","tcp_end":[0.44689,-0.0255,0.04768],"tcp_start":[0.45432,-0.02577,0.05497],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.46521,-0.0258,0.11281],"object_pos_start":[0.4585,-0.0257,0.02575],"object_to_goal_dist_end":0.28629,"object_to_goal_dist_start":0.30328,"object_z_max":0.1127,"peak_contact_force":0.10308,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19724.0,"raw_peak_contact_force":0.37523,"tcp_end":[0.45398,-0.02552,0.14013],"tcp_start":[0.44689,-0.0255,0.04768],"tcp_to_object_dist_end":0.02954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54887,0.10279,0.01602],"object_pos_start":[0.46521,-0.0258,0.11281],"object_to_goal_dist_end":0.16535,"object_to_goal_dist_start":0.28629,"object_z_max":0.14321,"peak_contact_force":0.12263,"phase_name":"transport_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13363.0,"raw_peak_contact_force":1.54085,"tcp_end":[0.60429,0.17692,0.23951],"tcp_start":[0.45398,-0.02552,0.14013],"tcp_to_object_dist_end":0.24189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.54887,0.10279,0.01602],"object_pos_start":[0.54887,0.10279,0.01602],"object_to_goal_dist_end":0.16535,"object_to_goal_dist_start":0.16535,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2616.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.62282,0.20287,0.1399],"tcp_start":[0.60429,0.17692,0.23951],"tcp_to_object_dist_end":0.17558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54887,0.10279,0.01602],"object_pos_start":[0.54887,0.10279,0.01602],"object_to_goal_dist_end":0.16535,"object_to_goal_dist_start":0.16535,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61628,0.20061,0.15871],"tcp_start":[0.62282,0.20287,0.1399],"tcp_to_object_dist_end":0.18567,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```