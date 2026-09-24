## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3060 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2228 | 0.42 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.2227 | 0.41 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3481 | 0.42 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2235 | 0.42 | ❌ rejected |

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

## Current Skill (Q=0.306) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach
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
    - 0.0
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: descend_1
- id: grasp
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_1
- id: lift
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
    - 0.1
    tolerance: 0.02
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport
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
    - 0.05
    tolerance: 0.02
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: release
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
  subtask_id: release_1
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.306
- **task_score** (E): 0.414
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.208
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2543 |
| descend | 1.00 | 1.00 | 0.0043 |
| grasp | 0.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1407 |
| transport | 1.00 | 1.00 | 0.1996 |
| place_descend | 0.67 | 1.00 | 0.0191 |
| release | 1.00 | 1.00 | 0.0215 |
| retract | 1.00 | 1.00 | 0.0520 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.048) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / force_exceeded | (0.510, 0.016, 0.048)→(0.508, 0.017, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 81.142 | 0.123 |
| grasp | grasp | 0.00 / guard_failure | (0.503, 0.016, 0.039)→(0.503, 0.016, 0.039) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.025) | 0.236→0.237 | 1.00 / 43.000 | 0.180 | 0.249 |
| lift | lift | 1.00 / step_budget | (0.503, 0.016, 0.039)→(0.499, 0.016, 0.179) | (0.516, 0.017, 0.025)→(0.511, 0.017, 0.163) | 0.237→0.207 | 1.00 / 39.000 | 0.080 | 0.563 |
| transport | approach | 1.00 / step_budget | (0.499, 0.016, 0.179)→(0.598, 0.173, 0.196) | (0.511, 0.017, 0.163)→(0.601, 0.174, 0.175) | 0.207→0.017 | 1.00 / 39.333 | 0.075 | 0.276 |
| place_descend | descend | 0.67 / force_exceeded | (0.598, 0.173, 0.196)→(0.598, 0.173, 0.177) | (0.601, 0.174, 0.175)→(0.600, 0.175, 0.155) | 0.017→0.023 | 1.00 / 39.333 | 534.707 | 0.275 |
| release | release | 1.00 / step_budget | (0.598, 0.173, 0.177)→(0.592, 0.172, 0.197) | (0.600, 0.175, 0.155)→(0.589, 0.171, 0.023) | 0.023→0.145 | 1.00 / 4.000 | 0.127 | 1.438 |
| retract | retract | 1.00 / step_budget | (0.592, 0.172, 0.197)→(0.600, 0.177, 0.248) | (0.589, 0.171, 0.023)→(0.586, 0.170, 0.026) | 0.145→0.143 | 1.00 / 4.000 | 0.123 | 0.137 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.572
- phase_breakdown.approach_1_score: 0.676
- phase_breakdown.descend_1_score: 0.824
- phase_breakdown.transport_arc_score: 0.470
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.318
- grasp_place_fitness: 0.694

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.755
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.571
- **Median Q (composite search score)**: 0.300
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10563,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.16495,"descend.descend_force_threshold":8.46233,"lift.lift_height":0.1916,"place_descend.place_force_threshold":7.46921,"place_descend.place_speed":0.11936,"retract.retract_speed":0.16888,"transport.arc_height":0.09015,"transport.transport_speed":0.21296},"optimized_scores":{"best_composite_score":0.30004,"best_fitness_score":0.75504,"best_task_score":0.5707},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":375.0,"contact_point_centroid":[0.58373,0.17481,-0.00333],"force_p95":0.51658,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82043,"mean_force":0.18323,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59003,0.17526,0.1092]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.52784,0.02758,-0.00156],"force_p95":0.49285,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57477,"mean_force":0.10949,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51514,0.02752,0.04002]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9551.0,"contact_point_centroid":[0.51331,0.04658,0.12675],"force_p95":0.08608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36877,"mean_force":0.0616,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51273,0.02737,0.12402]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10502.0,"contact_point_centroid":[0.56286,0.0911,0.22621],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31477,"mean_force":0.05227,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55949,0.10999,0.2248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11779.0,"contact_point_centroid":[0.51428,0.00843,0.12329],"force_p95":0.08109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30904,"mean_force":0.05151,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51274,0.02737,0.12151]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5307,0.0306,-0.00232],"force_p95":0.1955,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26032,"mean_force":0.14509,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51699,0.02764,0.03889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9698.0,"contact_point_centroid":[0.55814,0.13149,0.2279],"force_p95":0.08168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24685,"mean_force":0.05432,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56111,0.11278,0.22477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8400.0,"contact_point_centroid":[0.60089,0.15896,0.11403],"force_p95":0.07214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22564,"mean_force":0.04958,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59633,0.17744,0.1146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7140.0,"contact_point_centroid":[0.59262,0.19608,0.11719],"force_p95":0.08204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21767,"mean_force":0.05594,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59633,0.17744,0.1146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6334.0,"contact_point_centroid":[0.51752,0.00865,0.04028],"force_p95":0.06897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15462,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51648,0.02761,0.03832]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51083,0.0136,0.17501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.59111,0.19543,0.10051],"force_p95":0.08231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13654,"mean_force":0.04779,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59478,0.17669,0.09831]},{"body_a":"world","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.58341,0.17476,-0.00199],"force_p95":0.12393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12475,"mean_force":0.12273,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59215,0.17584,0.15543]},{"body_a":"world","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52247,0.02787,0.04605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.59931,0.15818,0.09731],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10994,"mean_force":0.04234,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59477,0.17669,0.09831]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.51736,0.04705,0.04119],"force_p95":0.09225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09515,"mean_force":0.05465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02761,0.03833]}],"total_contact_groups":16},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58341,0.17476,0.02602],"final_tcp_position":[0.59655,0.17709,0.18898],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52352,0.02779,0.04814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":52.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.52174,0.02793,0.04431],"tcp_start":[0.52352,0.02779,0.04814],"tcp_to_object_dist_end":0.02048,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53059,0.02885,0.02507],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18532,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18613,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13080.0,"raw_peak_contact_force":0.26032,"subtask_id":"grasp_1","tcp_end":[0.51646,0.02761,0.03829],"tcp_start":[0.51646,0.02761,0.03829],"tcp_to_object_dist_end":0.01939,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.52543,0.02826,0.19308],"object_pos_start":[0.53061,0.02882,0.02512],"object_to_goal_dist_end":0.18871,"object_to_goal_dist_start":0.18532,"object_z_max":0.19281,"peak_contact_force":0.08237,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21417.0,"raw_peak_contact_force":0.57477,"tcp_end":[0.51324,0.02741,0.21038],"tcp_start":[0.51646,0.02761,0.03829],"tcp_to_object_dist_end":0.02118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.59494,0.17952,0.12593],"object_pos_start":[0.52543,0.02826,0.19308],"object_to_goal_dist_end":0.01904,"object_to_goal_dist_start":0.18871,"object_z_max":0.23222,"peak_contact_force":0.08026,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20200.0,"raw_peak_contact_force":0.31477,"subtask_id":"transport_arc","tcp_end":[0.59855,0.17877,0.14769],"tcp_start":[0.51324,0.02741,0.21038],"tcp_to_object_dist_end":0.02207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.59341,0.17829,0.0782],"object_pos_start":[0.59494,0.17952,0.12593],"object_to_goal_dist_end":0.03097,"object_to_goal_dist_start":0.01904,"object_z_max":0.12593,"peak_contact_force":0.08242,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15540.0,"raw_peak_contact_force":0.22564,"tcp_end":[0.59671,0.17724,0.10158],"tcp_start":[0.59855,0.17877,0.14769],"tcp_to_object_dist_end":0.02363,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5832,0.17474,0.02621],"object_pos_start":[0.59341,0.17829,0.0782],"object_to_goal_dist_end":0.08399,"object_to_goal_dist_start":0.03097,"object_z_max":0.0782,"peak_contact_force":0.12471,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2659.0,"raw_peak_contact_force":0.82043,"subtask_id":"release_1","tcp_end":[0.58984,0.17521,0.12267],"tcp_start":[0.59671,0.17724,0.10158],"tcp_to_object_dist_end":0.09669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":260.0,"n_steps_budget":600.0,"object_pos_end":[0.58341,0.17476,0.02602],"object_pos_start":[0.5832,0.17474,0.02621],"object_to_goal_dist_end":0.08413,"object_to_goal_dist_start":0.08399,"object_z_max":0.02621,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1040.0,"raw_peak_contact_force":0.12475,"tcp_end":[0.59655,0.17709,0.18898],"tcp_start":[0.58984,0.17521,0.12267],"tcp_to_object_dist_end":0.16351,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69672,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.29681,"descend.descend_force_threshold":6.72192,"lift.lift_height":0.12671,"place_descend.place_force_threshold":9.99859,"place_descend.place_speed":0.12012,"retract.retract_speed":0.0501,"transport.arc_height":0.02491,"transport.transport_speed":0.23227},"optimized_scores":{"best_composite_score":0.25439,"best_fitness_score":0.58439,"best_task_score":0.22541},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.56742,0.17239,-0.0092],"force_p95":1.33965,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00451,"mean_force":0.47402,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57371,0.17565,0.26323]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50044,-0.0143,-0.00142],"force_p95":0.4696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54248,"mean_force":0.12592,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49081,-0.01435,0.0407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6348.0,"contact_point_centroid":[0.48739,-0.03353,0.09562],"force_p95":0.07784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31594,"mean_force":0.05714,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48829,-0.01432,0.09315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7425.0,"contact_point_centroid":[0.4887,0.00472,0.09288],"force_p95":0.07419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30928,"mean_force":0.05023,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4883,-0.01433,0.09125]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1910.0,"contact_point_centroid":[0.57321,0.19412,0.25524],"force_p95":0.07813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30213,"mean_force":0.05285,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57763,0.1756,0.2518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12627.0,"contact_point_centroid":[0.53092,0.05416,0.21453],"force_p95":0.07739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24695,"mean_force":0.05137,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52857,0.07315,0.21273]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2170.0,"contact_point_centroid":[0.58296,0.15708,0.25362],"force_p95":0.06851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21488,"mean_force":0.0465,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57762,0.17554,0.25199]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50387,-0.01565,-0.00213],"force_p95":0.154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21101,"mean_force":0.13215,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49251,-0.01436,0.03981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12380.0,"contact_point_centroid":[0.52684,0.09285,0.21603],"force_p95":0.07715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19686,"mean_force":0.05147,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52897,0.07398,0.21329]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.56733,0.1723,-0.00204],"force_p95":0.14636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15471,"mean_force":0.1164,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57777,0.18026,0.29826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6387.0,"contact_point_centroid":[0.49234,0.00473,0.04082],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13999,"mean_force":0.04128,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01435,0.03928]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49897,-0.00695,0.1756]},{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49788,-0.01432,0.04665]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.58178,0.15807,0.24613],"force_p95":0.0676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10706,"mean_force":0.04068,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57666,0.1767,0.24489]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1210.0,"contact_point_centroid":[0.57142,0.19504,0.24806],"force_p95":0.07094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10643,"mean_force":0.04284,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57666,0.1767,0.24488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5374.0,"contact_point_centroid":[0.49131,-0.03364,0.04191],"force_p95":0.07676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07967,"mean_force":0.04939,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01435,0.03929]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56733,0.1723,0.02602],"final_tcp_position":[0.58299,0.18499,0.32871],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49907,-0.01423,0.04891],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":60.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49715,-0.01438,0.04481],"tcp_start":[0.49907,-0.01423,0.04891],"tcp_to_object_dist_end":0.01998,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01499,0.02561],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15108,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13565.0,"raw_peak_contact_force":0.21101,"subtask_id":"grasp_1","tcp_end":[0.492,-0.01435,0.03926],"tcp_start":[0.492,-0.01435,0.03926],"tcp_to_object_dist_end":0.01803,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":343.0,"n_steps_budget":810.0,"object_pos_end":[0.49931,-0.01473,0.13096],"object_pos_start":[0.50377,-0.01499,0.02563],"object_to_goal_dist_end":0.24955,"object_to_goal_dist_start":0.31208,"object_z_max":0.13069,"peak_contact_force":0.07174,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13850.0,"raw_peak_contact_force":0.54248,"tcp_end":[0.48827,-0.01432,0.14657],"tcp_start":[0.492,-0.01435,0.03926],"tcp_to_object_dist_end":0.01913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.58615,0.17615,0.23923],"object_pos_start":[0.49931,-0.01473,0.13096],"object_to_goal_dist_end":0.0144,"object_to_goal_dist_start":0.24955,"object_z_max":0.2392,"peak_contact_force":0.07741,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25007.0,"raw_peak_contact_force":0.24695,"subtask_id":"transport_arc","tcp_end":[0.57762,0.17303,0.25797],"tcp_start":[0.48827,-0.01432,0.14657],"tcp_to_object_dist_end":0.02082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":99.0,"n_steps_budget":1000.0,"object_pos_end":[0.58502,0.17997,0.22849],"object_pos_start":[0.58615,0.17615,0.23923],"object_to_goal_dist_end":0.02109,"object_to_goal_dist_start":0.0144,"object_z_max":0.23923,"peak_contact_force":30.94588,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4080.0,"raw_peak_contact_force":0.30213,"tcp_end":[0.57796,0.17704,0.24806],"tcp_start":[0.57762,0.17303,0.25797],"tcp_to_object_dist_end":0.02102,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57445,0.17485,0.01789],"object_pos_start":[0.58502,0.17997,0.22849],"object_to_goal_dist_end":0.2309,"object_to_goal_dist_start":0.02109,"object_z_max":0.22849,"peak_contact_force":0.16353,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2677.0,"raw_peak_contact_force":2.00451,"subtask_id":"release_1","tcp_end":[0.57367,0.17565,0.26955],"tcp_start":[0.57796,0.17704,0.24806],"tcp_to_object_dist_end":0.25165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.56733,0.1723,0.02602],"object_pos_start":[0.57445,0.17485,0.01789],"object_to_goal_dist_end":0.22347,"object_to_goal_dist_start":0.2309,"object_z_max":0.02702,"peak_contact_force":0.12286,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.15471,"tcp_end":[0.58299,0.18499,0.32871],"tcp_start":[0.57367,0.17565,0.26955],"tcp_to_object_dist_end":0.30336,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84211,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13493,"descend.descend_force_threshold":5.95027,"lift.lift_height":0.16206,"place_descend.place_force_threshold":6.74585,"place_descend.place_speed":0.07758,"retract.retract_speed":0.17765,"transport.arc_height":0.08244,"transport.transport_speed":0.14588},"optimized_scores":{"best_composite_score":0.36365,"best_fitness_score":0.69365,"best_task_score":0.44639},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":246.0,"contact_point_centroid":[0.60789,0.16303,-0.00606],"force_p95":0.90057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49031,"mean_force":0.28669,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61259,0.16417,0.19048]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50953,0.03535,-0.00165],"force_p95":0.49644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57156,"mean_force":0.11537,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49886,0.03558,0.04074]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7762.0,"contact_point_centroid":[0.49635,0.05462,0.11181],"force_p95":0.08895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35904,"mean_force":0.06184,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49647,0.0354,0.10929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9859.0,"contact_point_centroid":[0.49763,0.01645,0.11008],"force_p95":0.08107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29784,"mean_force":0.04999,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49648,0.0354,0.10857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21.0,"contact_point_centroid":[0.61333,0.18398,0.18445],"force_p95":0.26953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29619,"mean_force":0.17303,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61868,0.16574,0.18105]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51277,0.03946,-0.00241],"force_p95":0.21343,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27459,"mean_force":0.15086,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5007,0.03574,0.03944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11670.0,"contact_point_centroid":[0.55379,0.07537,0.22548],"force_p95":0.08643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26634,"mean_force":0.05304,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55092,0.0943,0.22386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22.0,"contact_point_centroid":[0.62217,0.1467,0.18189],"force_p95":0.24655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25739,"mean_force":0.14051,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61868,0.16574,0.18105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10780.0,"contact_point_centroid":[0.55184,0.11683,0.22785],"force_p95":0.08402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22791,"mean_force":0.05573,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55447,0.09802,0.22477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1049.0,"contact_point_centroid":[0.61273,0.18407,0.17829],"force_p95":0.07852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19556,"mean_force":0.04981,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61631,0.16532,0.17543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6311.0,"contact_point_centroid":[0.50115,0.01672,0.04026],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17984,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5002,0.0357,0.03889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1237.0,"contact_point_centroid":[0.62055,0.14658,0.17537],"force_p95":0.07197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17279,"mean_force":0.04361,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61631,0.16532,0.17544]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50269,0.01759,0.17489]},{"body_a":"world","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.60788,0.16316,-0.00193],"force_p95":0.13165,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13261,"mean_force":0.11979,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61644,0.16686,0.21237]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50609,0.03598,0.04632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4987.0,"contact_point_centroid":[0.50031,0.05518,0.04118],"force_p95":0.0928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09909,"mean_force":0.05485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50021,0.0357,0.0389]}],"total_contact_groups":16},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6079,0.16316,0.02602],"final_tcp_position":[0.6211,0.1697,0.22643],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50718,0.03587,0.04843],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":56.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.50537,0.03607,0.04458],"tcp_start":[0.50718,0.03587,0.04843],"tcp_to_object_dist_end":0.02022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51268,0.03723,0.02481],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21437,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.20205,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13102.0,"raw_peak_contact_force":0.27459,"subtask_id":"grasp_1","tcp_end":[0.50018,0.0357,0.03887],"tcp_start":[0.50018,0.0357,0.03887],"tcp_to_object_dist_end":0.01887,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50814,0.03656,0.16466],"object_pos_start":[0.5127,0.03717,0.02488],"object_to_goal_dist_end":0.18203,"object_to_goal_dist_start":0.21436,"object_z_max":0.16439,"peak_contact_force":0.08456,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17708.0,"raw_peak_contact_force":0.57156,"tcp_end":[0.49674,0.03543,0.18149],"tcp_start":[0.50018,0.0357,0.03887],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.621,0.16768,0.15941],"object_pos_start":[0.50814,0.03656,0.16466],"object_to_goal_dist_end":0.01654,"object_to_goal_dist_start":0.18203,"object_z_max":0.22855,"peak_contact_force":0.06785,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22450.0,"raw_peak_contact_force":0.26634,"subtask_id":"transport_arc","tcp_end":[0.61868,0.16574,0.18105],"tcp_start":[0.49674,0.03543,0.18149],"tcp_to_object_dist_end":0.02186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.62081,0.16772,0.15882],"object_pos_start":[0.621,0.16768,0.15941],"object_to_goal_dist_end":0.01609,"object_to_goal_dist_start":0.01654,"object_z_max":0.15941,"peak_contact_force":1573.09317,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":43.0,"raw_peak_contact_force":0.29619,"tcp_end":[0.61862,0.1658,0.18051],"tcp_start":[0.61868,0.16574,0.18105],"tcp_to_object_dist_end":0.02189,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60872,0.16342,0.02578],"object_pos_start":[0.62081,0.16772,0.15882],"object_to_goal_dist_end":0.12106,"object_to_goal_dist_start":0.01609,"object_z_max":0.15882,"peak_contact_force":0.09158,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2532.0,"raw_peak_contact_force":1.49031,"subtask_id":"release_1","tcp_end":[0.61252,0.16416,0.19972],"tcp_start":[0.61862,0.1658,0.18051],"tcp_to_object_dist_end":0.17398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":133.0,"n_steps_budget":600.0,"object_pos_end":[0.6079,0.16316,0.02602],"object_pos_start":[0.60872,0.16342,0.02578],"object_to_goal_dist_end":0.12098,"object_to_goal_dist_start":0.12106,"object_z_max":0.02659,"peak_contact_force":0.1234,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":532.0,"raw_peak_contact_force":0.13261,"tcp_end":[0.6211,0.1697,0.22643],"tcp_start":[0.61252,0.16416,0.19972],"tcp_to_object_dist_end":0.20095,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```