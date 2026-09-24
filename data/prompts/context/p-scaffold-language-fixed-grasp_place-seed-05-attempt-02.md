## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1790 | 0.41 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1731 | 0.41 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2807 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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

## Current Skill (Q=0.179) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
- id: release_1
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: none
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
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
    - 0.15
    orientation:
      mode: none
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
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
    - 0.15
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: descend_goal
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: placement_force
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05]
  - orientation: mode=none
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=placement_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.179
- **task_score** (E): 0.411
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0628 |
| descend_1 | 1.00 | 1.00 | 0.2028 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 0.33 | 1.00 | 0.1316 |
| transport_1 | 0.00 | 1.00 | 0.1218 |
| descend_goal | 1.00 | 1.00 | 0.1130 |
| release_1 | 1.00 | 1.00 | 0.0217 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.248) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.016, 0.248)→(0.510, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 11.650 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.018, 0.045)→(0.502, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.667 | 0.148 | 0.197 |
| lift_1 | lift | 0.33 / step_budget | (0.502, 0.018, 0.036)→(0.498, 0.017, 0.167) | (0.516, 0.018, 0.026)→(0.508, 0.018, 0.150) | 0.236→0.198 | 1.00 / 32.667 | 0.089 | 0.583 |
| transport_1 | approach | 0.00 / step_budget | (0.498, 0.017, 0.167)→(0.548, 0.101, 0.238) | (0.508, 0.018, 0.150)→(0.554, 0.103, 0.215) | 0.198→0.111 | 1.00 / 36.667 | 0.086 | 0.169 |
| descend_goal | descend | 1.00 / step_budget | (0.548, 0.101, 0.238)→(0.599, 0.174, 0.176) | (0.554, 0.103, 0.215)→(0.595, 0.175, 0.148) | 0.111→0.023 | 1.00 / 32.000 | 0.098 | 0.228 |
| release_1 | release | 1.00 / step_budget | (0.599, 0.174, 0.176)→(0.593, 0.173, 0.197) | (0.595, 0.175, 0.148)→(0.589, 0.175, 0.024) | 0.023→0.145 | 1.00 / 3.000 | 0.192 | 1.419 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.571
- phase_score: 0.350
- phase_breakdown.transport_arc_score: 0.102
- phase_breakdown.descend_1_score: 0.859
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.384
- phase_breakdown.approach_1_score: 0.007
- grasp_place_fitness: 0.759

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.759
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.571
- **Median Q (composite search score)**: 0.197
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86719,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24269,"descend_1.depth":0.01024,"descend_goal.place_z_offset":0.02424,"lift_1.lift_height":0.12157,"lift_1.speed":0.1312,"transport_1.speed":0.15942,"transport_1.transport_height":0.1391},"optimized_scores":{"best_composite_score":0.25911,"best_fitness_score":0.75911,"best_task_score":0.57082},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.57305,0.18628,-0.00802],"force_p95":1.1925,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27146,"mean_force":0.48921,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58753,0.17048,0.14038]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.52742,0.02947,-0.00126],"force_p95":0.33339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60228,"mean_force":0.09509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51462,0.02944,0.03626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7653.0,"contact_point_centroid":[0.51449,0.04844,0.08195],"force_p95":0.10844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34194,"mean_force":0.07207,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51222,0.02929,0.07932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10214.0,"contact_point_centroid":[0.51479,0.01063,0.08179],"force_p95":0.09747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31862,"mean_force":0.05601,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51221,0.02929,0.08052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1310.0,"contact_point_centroid":[0.58673,0.19046,0.12817],"force_p95":0.11613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28943,"mean_force":0.05689,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59155,0.17174,0.12806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1212.0,"contact_point_centroid":[0.59621,0.15347,0.12597],"force_p95":0.07791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27609,"mean_force":0.04888,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59183,0.17183,0.12845]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5386.0,"contact_point_centroid":[0.58794,0.1334,0.16405],"force_p95":0.10464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26504,"mean_force":0.06784,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58077,0.15109,0.16493]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5380.0,"contact_point_centroid":[0.5796,0.16998,0.16613],"force_p95":0.09666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23865,"mean_force":0.06606,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58073,0.15101,0.16508]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14233.0,"contact_point_centroid":[0.54651,0.0633,0.17252],"force_p95":0.09978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23242,"mean_force":0.06857,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54001,0.08105,0.17248]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.00211],"force_p95":0.15292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2107,"mean_force":0.1306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51768,0.02965,0.03605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11974.0,"contact_point_centroid":[0.54238,0.10123,0.17491],"force_p95":0.10997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20554,"mean_force":0.07827,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54072,0.08222,0.1733]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.5175,0.01054,0.03654],"force_p95":0.0675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16953,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51643,0.02957,0.03462]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.5305,0.03079,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51071,0.01279,0.28841]},{"body_a":"world","body_b":"grasp_target","contact_count":2764.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52267,0.02764,0.15862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.51694,0.04888,0.03745],"force_p95":0.08164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08436,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51643,0.02957,0.03463]}],"total_contact_groups":15},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58955,0.18733,0.02531],"final_tcp_position":[0.5939,0.17221,0.13208],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":34.70445,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":848.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52245,0.02527,0.27476],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":691.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":34.70445,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2764.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52515,0.03014,0.04464],"tcp_start":[0.52245,0.02527,0.27476],"tcp_to_object_dist_end":0.01939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03015,0.02562],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18408,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15119,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11291.0,"raw_peak_contact_force":0.2107,"subtask_id":"grasp_1","tcp_end":[0.5164,0.02957,0.03459],"tcp_start":[0.52515,0.03014,0.04464],"tcp_to_object_dist_end":0.01667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.52646,0.03004,0.12458],"object_pos_start":[0.53044,0.03015,0.02562],"object_to_goal_dist_end":0.16725,"object_to_goal_dist_start":0.18408,"object_z_max":0.12443,"peak_contact_force":0.1062,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18033.0,"raw_peak_contact_force":0.60228,"tcp_end":[0.51245,0.02931,0.14184],"tcp_start":[0.5164,0.02957,0.03459],"tcp_to_object_dist_end":0.02224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57657,0.13104,0.18044],"object_pos_start":[0.52646,0.03004,0.12458],"object_to_goal_dist_end":0.0901,"object_to_goal_dist_start":0.16725,"object_z_max":0.18041,"peak_contact_force":0.10242,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26207.0,"raw_peak_contact_force":0.23242,"subtask_id":"transport_arc","tcp_end":[0.56869,0.12872,0.20529],"tcp_start":[0.51245,0.02931,0.14184],"tcp_to_object_dist_end":0.02617,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.59298,0.17382,0.1037],"object_pos_start":[0.57657,0.13104,0.18044],"object_to_goal_dist_end":0.01073,"object_to_goal_dist_start":0.0901,"object_z_max":0.18044,"peak_contact_force":0.08381,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10766.0,"raw_peak_contact_force":0.26504,"tcp_end":[0.5939,0.17221,0.13208],"tcp_start":[0.56869,0.12872,0.20529],"tcp_to_object_dist_end":0.02845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58955,0.18733,0.02531],"object_pos_start":[0.59298,0.17382,0.1037],"object_to_goal_dist_end":0.0841,"object_to_goal_dist_start":0.01073,"object_z_max":0.1037,"peak_contact_force":0.33646,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2660.0,"raw_peak_contact_force":1.27146,"subtask_id":"release_1","tcp_end":[0.58741,0.17045,0.15309],"tcp_start":[0.5939,0.17221,0.13208],"tcp_to_object_dist_end":0.12891,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0219,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17486,"descend_1.depth":0.0116,"descend_goal.place_z_offset":0.00056,"lift_1.lift_height":0.2048,"lift_1.speed":0.08186,"transport_1.speed":0.1954,"transport_1.transport_height":0.14477},"optimized_scores":{"best_composite_score":0.08125,"best_fitness_score":0.58125,"best_task_score":0.2173},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.56473,0.17633,-0.0084],"force_p95":1.22723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6114,"mean_force":0.43182,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57707,0.18059,0.25701]},{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.49993,-0.01509,-0.00117],"force_p95":0.34017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54863,"mean_force":0.09621,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4886,-0.01511,0.03841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20692.0,"contact_point_centroid":[0.48718,0.00396,0.10141],"force_p95":0.07301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31316,"mean_force":0.04952,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48605,-0.01508,0.09952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18289.0,"contact_point_centroid":[0.48629,-0.03425,0.10322],"force_p95":0.07886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31261,"mean_force":0.05485,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48604,-0.01508,0.10056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.57509,0.20011,0.23937],"force_p95":0.08878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23181,"mean_force":0.05572,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58005,0.18169,0.2391]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12682.0,"contact_point_centroid":[0.55515,0.15749,0.25957],"force_p95":0.07647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19486,"mean_force":0.05198,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55926,0.13889,0.25724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14174.0,"contact_point_centroid":[0.56236,0.11902,0.25829],"force_p95":0.07527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19421,"mean_force":0.04766,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5587,0.13781,0.25759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1067.0,"contact_point_centroid":[0.5844,0.16331,0.23702],"force_p95":0.07844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1911,"mean_force":0.05022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58005,0.18169,0.23909]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01573,-0.00204],"force_p95":0.13752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17276,"mean_force":0.12641,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49149,-0.01513,0.03818]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.13649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49917,-0.0004,0.25579]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18864.0,"contact_point_centroid":[0.51351,0.02123,0.22596],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13147,"mean_force":0.05156,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51083,0.04013,0.22405]},{"body_a":"world","body_b":"grasp_target","contact_count":2048.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49812,-0.01244,0.12826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18570.0,"contact_point_centroid":[0.51049,0.05823,0.22519],"force_p95":0.07693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12025,"mean_force":0.05319,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51031,0.03913,0.22294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.49125,0.00393,0.03864],"force_p95":0.06669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10181,"mean_force":0.04258,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49027,-0.01512,0.03688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4164.0,"contact_point_centroid":[0.48963,-0.03437,0.03943],"force_p95":0.07841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09036,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49027,-0.01512,0.03689]}],"total_contact_groups":15},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56951,0.17753,0.02002],"final_tcp_position":[0.58144,0.18196,0.24238],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.6114,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1104.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49999,-0.00976,0.21188],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2048.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49876,-0.01517,0.04603],"tcp_start":[0.49999,-0.00976,0.21188],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01559,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31235,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13702,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11089.0,"raw_peak_contact_force":0.17276,"subtask_id":"grasp_1","tcp_end":[0.49024,-0.01512,0.03685],"tcp_start":[0.49876,-0.01517,0.04603],"tcp_to_object_dist_end":0.01741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49456,-0.01536,0.1504],"object_pos_start":[0.50371,-0.01559,0.02582],"object_to_goal_dist_end":0.24333,"object_to_goal_dist_start":0.31235,"object_z_max":0.15025,"peak_contact_force":0.07973,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39139.0,"raw_peak_contact_force":0.54863,"tcp_end":[0.48639,-0.01507,0.16823],"tcp_start":[0.49024,-0.01512,0.03685],"tcp_to_object_dist_end":0.01961,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54347,0.09197,0.25706],"object_pos_start":[0.49456,-0.01536,0.1504],"object_to_goal_dist_end":0.10528,"object_to_goal_dist_start":0.24333,"object_z_max":0.25697,"peak_contact_force":0.0767,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37434.0,"raw_peak_contact_force":0.13147,"subtask_id":"transport_arc","tcp_end":[0.53627,0.09049,0.27927],"tcp_start":[0.48639,-0.01507,0.16823],"tcp_to_object_dist_end":0.02339,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.57726,0.18227,0.21512],"object_pos_start":[0.54347,0.09197,0.25706],"object_to_goal_dist_end":0.03476,"object_to_goal_dist_start":0.10528,"object_z_max":0.25708,"peak_contact_force":0.08967,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26856.0,"raw_peak_contact_force":0.19486,"tcp_end":[0.58144,0.18196,0.24238],"tcp_start":[0.53627,0.09049,0.27927],"tcp_to_object_dist_end":0.02758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56951,0.17753,0.02002],"object_pos_start":[0.57726,0.18227,0.21512],"object_to_goal_dist_end":0.22897,"object_to_goal_dist_start":0.03476,"object_z_max":0.21512,"peak_contact_force":0.12048,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2181.0,"raw_peak_contact_force":1.6114,"subtask_id":"release_1","tcp_end":[0.57704,0.18059,0.26373],"tcp_start":[0.58144,0.18196,0.24238],"tcp_to_object_dist_end":0.24384,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68208,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22036,"descend_1.depth":0.01016,"descend_goal.place_z_offset":0.01526,"lift_1.lift_height":0.25713,"lift_1.speed":0.09628,"transport_1.speed":0.04273,"transport_1.transport_height":0.17816},"optimized_scores":{"best_composite_score":0.19675,"best_fitness_score":0.69675,"best_task_score":0.44626},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":281.0,"contact_point_centroid":[0.60764,0.15943,-0.00486],"force_p95":0.78684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37316,"mean_force":0.24179,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61497,0.16738,0.16343]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.50899,0.03754,-0.00122],"force_p95":0.40167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59687,"mean_force":0.09463,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49725,0.03813,0.03708]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49501,0.05714,0.11465],"force_p95":0.08348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34099,"mean_force":0.05885,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49476,0.03794,0.1119]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20693.0,"contact_point_centroid":[0.49666,0.01902,0.11205],"force_p95":0.07824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31565,"mean_force":0.04981,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49476,0.03794,0.11044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":657.0,"contact_point_centroid":[0.61548,0.1873,0.14849],"force_p95":0.11909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24604,"mean_force":0.07532,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61917,0.16863,0.15005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.62265,0.15056,0.14609],"force_p95":0.09371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22528,"mean_force":0.05718,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61913,0.16862,0.14998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18514.0,"contact_point_centroid":[0.58281,0.10924,0.18785],"force_p95":0.08013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22513,"mean_force":0.05003,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.57976,0.12806,0.1877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16294.0,"contact_point_centroid":[0.57686,0.1473,0.18942],"force_p95":0.08527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22249,"mean_force":0.05512,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58025,0.12854,0.18731]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.0397,-0.00212],"force_p95":0.1579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20844,"mean_force":0.13192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5001,0.03837,0.03658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.50048,0.01926,0.03671],"force_p95":0.07369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17812,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49887,0.03827,0.03524]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17020.0,"contact_point_centroid":[0.51643,0.08223,0.21302],"force_p95":0.07884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14398,"mean_force":0.05731,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51702,0.06309,0.21032]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.51251,0.03972,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50347,0.01756,0.28026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19787.0,"contact_point_centroid":[0.5201,0.04419,0.21144],"force_p95":0.07258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13094,"mean_force":0.04927,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51686,0.06293,0.21017]},{"body_a":"world","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50649,0.03634,0.14969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4216.0,"contact_point_centroid":[0.49906,0.05757,0.03792],"force_p95":0.08411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08899,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49888,0.03827,0.03524]}],"total_contact_groups":15},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60746,0.15973,0.02637],"final_tcp_position":[0.62097,0.16904,0.15363],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.37316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50789,0.03388,0.25678],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2584.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50744,0.03896,0.0447],"tcp_start":[0.50789,0.03388,0.25678],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03894,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21297,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1556,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11049.0,"raw_peak_contact_force":0.20844,"subtask_id":"grasp_1","tcp_end":[0.49884,0.03827,0.0352],"tcp_start":[0.50744,0.03896,0.0447],"tcp_to_object_dist_end":0.01673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50394,0.03877,0.17364],"object_pos_start":[0.5125,0.03894,0.02556],"object_to_goal_dist_end":0.18437,"object_to_goal_dist_start":0.21297,"object_z_max":0.17346,"peak_contact_force":0.08109,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37840.0,"raw_peak_contact_force":0.59687,"tcp_end":[0.4952,0.03798,0.19107],"tcp_start":[0.49884,0.03827,0.0352],"tcp_to_object_dist_end":0.01951,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.543,0.08513,0.20788],"object_pos_start":[0.50394,0.03877,0.17364],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.18437,"object_z_max":0.20785,"peak_contact_force":0.07754,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36807.0,"raw_peak_contact_force":0.14398,"subtask_id":"transport_arc","tcp_end":[0.53758,0.08391,0.23013],"tcp_start":[0.4952,0.03798,0.19107],"tcp_to_object_dist_end":0.02293,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.61591,0.16975,0.12448],"object_pos_start":[0.543,0.08513,0.20788],"object_to_goal_dist_end":0.02378,"object_to_goal_dist_start":0.13689,"object_z_max":0.20788,"peak_contact_force":0.11962,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34808.0,"raw_peak_contact_force":0.22513,"tcp_end":[0.62097,0.16904,0.15363],"tcp_start":[0.53758,0.08391,0.23013],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60746,0.15973,0.02637],"object_pos_start":[0.61591,0.16975,0.12448],"object_to_goal_dist_end":0.12103,"object_to_goal_dist_start":0.02378,"object_z_max":0.12448,"peak_contact_force":0.1191,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1894.0,"raw_peak_contact_force":1.37316,"subtask_id":"release_1","tcp_end":[0.61489,0.16736,0.17388],"tcp_start":[0.62097,0.16904,0.15363],"tcp_to_object_dist_end":0.1479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```