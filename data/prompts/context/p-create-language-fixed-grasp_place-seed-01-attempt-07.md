## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2555 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3705 | 0.32 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 2 | 0.3628 | 0.24 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2461 | 0.19 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1654 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.256) — your mutation base

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

- **Composite score**: 0.256
- **task_score** (E): 0.186
- **fitness_score**: 0.556  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1863 |
| descend_1 | 1.00 | 1.00 | 0.0645 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 1.00 | 1.00 | 0.1348 |
| transport_to_goal | 0.00 | 1.00 | 0.0012 |
| descend_to_goal | 0.00 | 1.00 | 0.1519 |
| release_1 | 1.00 | 1.00 | 0.0233 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.119) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.000, 0.119)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.146 | 0.197 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.047)→(0.474, -0.001, 0.181) | (0.479, -0.001, 0.026)→(0.484, -0.001, 0.151) | 0.278→0.244 | 1.00 / 14.000 | 524.478 | 0.393 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.481, 0.010, 0.200)→(0.481, 0.010, 0.201) | (0.484, -0.001, 0.151)→(0.484, 0.000, 0.151) | 0.244→0.243 | 1.00 / 4.667 | 0.016 | 0.320 |
| descend_to_goal | descend | 0.00 / step_budget | (0.481, 0.010, 0.201)→(0.555, 0.133, 0.161) | (0.491, 0.011, 0.166)→(0.507, 0.019, 0.016) | 0.232→0.254 | 1.00 / 8.000 | 3249.666 | 1.736 |
| release_1 | release | 1.00 / step_budget | (0.555, 0.133, 0.161)→(0.549, 0.132, 0.184) | (0.507, 0.019, 0.016)→(0.507, 0.019, 0.016) | 0.254→0.254 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.219
- phase_score: 0.459
- phase_breakdown.release_1_score: 0.256
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.transport_arc_score: 0.317
- phase_breakdown.approach_1_score: 0.171
- grasp_place_fitness: 0.573

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.573
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.219
- **Median Q (composite search score)**: 0.259
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.191


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88406,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.18964,"transport_to_goal.arc_height":0.1309,"transport_to_goal.transport_speed":0.32502},"optimized_scores":{"best_composite_score":0.27263,"best_fitness_score":0.57263,"best_task_score":0.21934},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3683.0,"contact_point_centroid":[0.51731,0.06466,-0.00229],"force_p95":0.12426,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93824,"mean_force":0.13472,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52177,0.12864,0.17381]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.49899,0.04233,-0.00125],"force_p95":0.25607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4178,"mean_force":0.05668,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48684,0.04313,0.04761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.50303,0.05999,0.19789],"force_p95":0.2708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35281,"mean_force":0.15359,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49686,0.04337,0.20369]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14394.0,"contact_point_centroid":[0.49314,0.06195,0.11209],"force_p95":0.10816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28735,"mean_force":0.06774,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48962,0.04313,0.11106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13402.0,"contact_point_centroid":[0.49313,0.02429,0.11422],"force_p95":0.11167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26676,"mean_force":0.07111,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48981,0.04314,0.11357]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04492,-0.00215],"force_p95":0.16399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22302,"mean_force":0.1335,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48927,0.04337,0.04693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.50422,0.02621,0.19638],"force_p95":0.17456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1762,"mean_force":0.12961,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49712,0.04343,0.20311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.48842,0.02404,0.0475],"force_p95":0.07795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13945,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.0457]},{"body_a":"world","body_b":"grasp_target","contact_count":2296.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49758,0.0204,0.20872]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49548,0.04263,0.08617]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51731,0.06467,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53903,0.19083,0.15672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18.0,"contact_point_centroid":[0.5034,0.05842,0.19802],"force_p95":0.11035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11035,"mean_force":0.0555,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.49628,0.04333,0.20491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5271.0,"contact_point_centroid":[0.48881,0.06245,0.04779],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07405,"mean_force":0.04219,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04327,0.04571]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3696.0,"contact_point_centroid":[0.52348,0.13245,0.17487],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01055,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52302,0.13243,0.17264]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.54246,0.19193,0.15414],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.0099,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54169,0.1919,0.15198]}],"total_contact_groups":15},"final_pose_error":0.05737,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.51731,0.06467,0.01602],"final_tcp_position":[0.5432,0.19213,0.15455],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9748.75319,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49718,0.04149,0.11825],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":832.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49602,0.04398,0.05434],"tcp_start":[0.49718,0.04149,0.11825],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04379,0.02547],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24321,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16032,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11401.0,"raw_peak_contact_force":0.22302,"subtask_id":"grasp_1","tcp_end":[0.48811,0.04327,0.04567],"tcp_start":[0.49602,0.04398,0.05434],"tcp_to_object_dist_end":0.02405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.50555,0.04403,0.17168],"object_pos_start":[0.50115,0.04379,0.02547],"object_to_goal_dist_end":0.21076,"object_to_goal_dist_start":0.24321,"object_z_max":0.17172,"peak_contact_force":0.23765,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27942.0,"raw_peak_contact_force":0.4178,"tcp_end":[0.49719,0.04345,0.20282],"tcp_start":[0.48811,0.04327,0.04567],"tcp_to_object_dist_end":0.03224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50609,0.04592,0.17073],"object_pos_start":[0.50555,0.04403,0.17168],"object_to_goal_dist_end":0.2087,"object_to_goal_dist_start":0.21076,"object_z_max":0.17168,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":87.0,"raw_peak_contact_force":0.35281,"tcp_end":[0.49625,0.04321,0.20493],"tcp_start":[0.4964,0.04324,0.20474],"tcp_to_object_dist_end":0.03569,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51731,0.06467,0.01602],"object_pos_start":[0.5065,0.04704,0.16932],"object_to_goal_dist_end":0.22757,"object_to_goal_dist_start":0.20736,"object_z_max":0.16932,"peak_contact_force":9748.75319,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7397.0,"raw_peak_contact_force":1.93824,"subtask_id":"transport_arc","tcp_end":[0.5432,0.19213,0.15455],"tcp_start":[0.49625,0.04321,0.20493],"tcp_to_object_dist_end":0.19002,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51731,0.06467,0.01602],"object_pos_start":[0.51731,0.06467,0.01602],"object_to_goal_dist_end":0.22757,"object_to_goal_dist_start":0.22757,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.53744,0.1902,0.177],"tcp_start":[0.5432,0.19213,0.15455],"tcp_to_object_dist_end":0.20513,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86154,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.18572,"transport_to_goal.arc_height":0.12949,"transport_to_goal.transport_speed":0.33326},"optimized_scores":{"best_composite_score":0.23471,"best_fitness_score":0.53471,"best_task_score":0.1446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3668.0,"contact_point_centroid":[0.49101,-0.02562,-0.00229],"force_p95":0.12704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63099,"mean_force":0.13612,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5205,0.03926,0.19213]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.47437,-0.01918,-0.0011],"force_p95":0.26538,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38716,"mean_force":0.0469,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46271,-0.01953,0.04882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":26.0,"contact_point_centroid":[0.47905,-0.00186,0.19338],"force_p95":0.26289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28029,"mean_force":0.17634,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47206,-0.01965,0.20011]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.47782,-0.03606,0.19631],"force_p95":0.25158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27663,"mean_force":0.10477,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47144,-0.01987,0.20068]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13366.0,"contact_point_centroid":[0.46847,-0.00062,0.11271],"force_p95":0.11488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27238,"mean_force":0.07151,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46522,-0.01952,0.11196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14857.0,"contact_point_centroid":[0.4684,-0.0383,0.11348],"force_p95":0.10007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26492,"mean_force":0.06514,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46529,-0.01952,0.11287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7.0,"contact_point_centroid":[0.47717,-0.03443,0.19502],"force_p95":0.22703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23764,"mean_force":0.13751,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.47027,-0.02043,0.20225]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13758,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17752,"mean_force":0.12663,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46499,-0.01959,0.0481]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48633,-0.00907,0.2097]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47183,-0.01908,0.08713]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49102,-0.02561,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55488,0.08133,0.19065]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.46342,-0.00031,0.04912],"force_p95":0.06792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09914,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01956,0.047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5391.0,"contact_point_centroid":[0.46347,-0.03878,0.04883],"force_p95":0.06505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0819,"mean_force":0.041,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01956,0.047]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3651.0,"contact_point_centroid":[0.52322,0.04203,0.19409],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01562,"mean_force":0.01061,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52297,0.04203,0.19186]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.55784,0.0818,0.18823],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01026,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55747,0.0818,0.18589]}],"total_contact_groups":15},"final_pose_error":0.10611,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.49102,-0.02561,0.01602],"final_tcp_position":[0.55878,0.08186,0.18829],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47418,-0.01851,0.11955],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":856.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47153,-0.01974,0.05481],"tcp_start":[0.47418,-0.01851,0.11955],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13643,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.17752,"subtask_id":"grasp_1","tcp_end":[0.46387,-0.01956,0.04697],"tcp_start":[0.47153,-0.01974,0.05481],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.48063,-0.01981,0.16861],"object_pos_start":[0.47609,-0.01971,0.0258],"object_to_goal_dist_end":0.23503,"object_to_goal_dist_start":0.28827,"object_z_max":0.16863,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28356.0,"raw_peak_contact_force":0.38716,"tcp_end":[0.47218,-0.0196,0.19991],"tcp_start":[0.46387,-0.01956,0.04697],"tcp_to_object_dist_end":0.03242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.48071,-0.01992,0.16853],"object_pos_start":[0.48063,-0.01981,0.16861],"object_to_goal_dist_end":0.23507,"object_to_goal_dist_start":0.23503,"object_z_max":0.16861,"peak_contact_force":0.00784,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":102.0,"raw_peak_contact_force":0.28029,"tcp_end":[0.47027,-0.02039,0.20213],"tcp_start":[0.47158,-0.01979,0.20051],"tcp_to_object_dist_end":0.0352,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49102,-0.02561,0.01602],"object_pos_start":[0.48109,-0.02231,0.16618],"object_to_goal_dist_end":0.29007,"object_to_goal_dist_start":0.23688,"object_z_max":0.16618,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7326.0,"raw_peak_contact_force":1.63099,"subtask_id":"transport_arc","tcp_end":[0.55878,0.08186,0.18829],"tcp_start":[0.47027,-0.02039,0.20213],"tcp_to_object_dist_end":0.21406,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49102,-0.02561,0.01602],"object_pos_start":[0.49102,-0.02561,0.01602],"object_to_goal_dist_end":0.29007,"object_to_goal_dist_start":0.29007,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55338,0.08107,0.21098],"tcp_start":[0.55878,0.08186,0.18829],"tcp_to_object_dist_end":0.23083,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92969,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.lift_height":0.12661,"transport_to_goal.arc_height":0.06764,"transport_to_goal.transport_speed":0.3344},"optimized_scores":{"best_composite_score":0.25917,"best_fitness_score":0.55917,"best_task_score":0.19459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3670.0,"contact_point_centroid":[0.51144,0.01692,-0.00227],"force_p95":0.12435,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6389,"mean_force":0.13446,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52482,0.07599,0.16141]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.45703,-0.02488,-0.00112],"force_p95":0.25376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3754,"mean_force":0.0405,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44587,-0.02545,0.04957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2673.0,"contact_point_centroid":[0.46658,-0.03141,0.16314],"force_p95":0.13387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32817,"mean_force":0.08311,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46075,-0.0129,0.16337]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2510.0,"contact_point_centroid":[0.46678,0.00572,0.16327],"force_p95":0.14535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31385,"mean_force":0.08885,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46076,-0.01292,0.16326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9628.0,"contact_point_centroid":[0.45009,-0.00642,0.08994],"force_p95":0.1029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26796,"mean_force":0.06403,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4482,-0.02543,0.08929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10733.0,"contact_point_centroid":[0.44987,-0.04436,0.09002],"force_p95":0.09545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25122,"mean_force":0.05833,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44821,-0.02543,0.08935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":32.0,"contact_point_centroid":[0.48291,0.02576,0.1884],"force_p95":0.20869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21678,"mean_force":0.09576,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.47603,0.00835,0.19523]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00207],"force_p95":0.14286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19114,"mean_force":0.12786,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44797,-0.02554,0.04873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.48296,-0.00895,0.18831],"force_p95":0.17282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18025,"mean_force":0.08671,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.47608,0.00842,0.19519]},{"body_a":"world","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4784,-0.01185,0.20979]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45518,-0.02493,0.0873]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5115,0.01693,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55803,0.12404,0.14256]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.44709,-0.00626,0.04884],"force_p95":0.0727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10424,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44691,-0.0255,0.0477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.44631,-0.04465,0.04879],"force_p95":0.06531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0767,"mean_force":0.04081,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44692,-0.0255,0.04771]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3588.0,"contact_point_centroid":[0.52807,0.07985,0.16202],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01066,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52777,0.07985,0.15973]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.56143,0.12479,0.13985],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56094,0.12478,0.13784]}],"total_contact_groups":16},"final_pose_error":0.11046,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.5115,0.01693,0.01602],"final_tcp_position":[0.56248,0.12494,0.14041],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.6389,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45796,-0.02419,0.11958],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":864.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45432,-0.02577,0.05497],"tcp_start":[0.45796,-0.02419,0.11958],"tcp_to_object_dist_end":0.02927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.0257,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1411,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11561.0,"raw_peak_contact_force":0.19114,"subtask_id":"grasp_1","tcp_end":[0.44689,-0.0255,0.04768],"tcp_start":[0.45432,-0.02577,0.05497],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.46501,-0.0258,0.11375],"object_pos_start":[0.4585,-0.0257,0.02575],"object_to_goal_dist_end":0.28641,"object_to_goal_dist_start":0.30328,"object_z_max":0.11364,"peak_contact_force":0.1029,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20495.0,"raw_peak_contact_force":0.3754,"tcp_end":[0.45401,-0.02552,0.14135],"tcp_start":[0.44689,-0.0255,0.04768],"tcp_to_object_dist_end":0.02971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.46508,-0.02543,0.11455],"object_pos_start":[0.46501,-0.0258,0.11375],"object_to_goal_dist_end":0.28606,"object_to_goal_dist_start":0.28641,"object_z_max":0.16348,"peak_contact_force":0.03987,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5183.0,"raw_peak_contact_force":0.32817,"tcp_end":[0.47579,0.00796,0.19527],"tcp_start":[0.47559,0.00725,0.19449],"tcp_to_object_dist_end":0.08801,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5115,0.01693,0.01602],"object_pos_start":[0.486,0.00764,0.16347],"object_to_goal_dist_end":0.24553,"object_to_goal_dist_start":0.25187,"object_z_max":0.16347,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7326.0,"raw_peak_contact_force":1.6389,"subtask_id":"transport_arc","tcp_end":[0.56248,0.12494,0.14041],"tcp_start":[0.47579,0.00796,0.19527],"tcp_to_object_dist_end":0.17245,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5115,0.01693,0.01602],"object_pos_start":[0.5115,0.01693,0.01602],"object_to_goal_dist_end":0.24553,"object_to_goal_dist_start":0.24553,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55629,0.12361,0.16282],"tcp_start":[0.56248,0.12494,0.14041],"tcp_to_object_dist_end":0.18691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```