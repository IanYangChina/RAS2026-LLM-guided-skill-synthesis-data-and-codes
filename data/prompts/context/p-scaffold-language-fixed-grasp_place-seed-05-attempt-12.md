## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0259 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.2014 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.1205 | 0.22 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.1203 | 0.22 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.1204 | 0.22 | ❌ rejected |

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

## Current Skill (Q=0.026) — your mutation base

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
    - 0.2
    orientation:
      mode: none
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
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
    - 0.15
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: descend_goal
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
    - 0.03
    orientation:
      mode: none
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: placement_force
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort

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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=none
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=placement_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0

## Design Metrics

- **Composite score**: 0.026
- **task_score** (E): 0.407
- **fitness_score**: 0.676  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0347 |
| descend_1 | 1.00 | 1.00 | 0.2489 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 1.00 | 1.00 | 0.1556 |
| transport_1 | 0.33 | 1.00 | 0.1768 |
| descend_goal | 1.00 | 1.00 | 0.1516 |
| release_1 | 1.00 | 1.00 | 0.0214 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.295) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.017, 0.295)→(0.510, 0.018, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.018, 0.046)→(0.502, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.333 | 0.146 | 0.188 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.018, 0.036)→(0.498, 0.017, 0.192) | (0.516, 0.018, 0.026)→(0.508, 0.018, 0.172) | 0.236→0.206 | 1.00 / 32.000 | 0.090 | 0.573 |
| transport_1 | approach | 0.33 / step_budget | (0.498, 0.017, 0.192)→(0.570, 0.120, 0.304) | (0.508, 0.018, 0.172)→(0.576, 0.122, 0.278) | 0.206→0.150 | 1.00 / 33.000 | 0.086 | 0.256 |
| descend_goal | descend | 1.00 / step_budget | (0.570, 0.120, 0.304)→(0.600, 0.176, 0.196) | (0.576, 0.122, 0.278)→(0.599, 0.177, 0.164) | 0.150→0.012 | 1.00 / 24.333 | 0.121 | 0.313 |
| release_1 | release | 1.00 / step_budget | (0.600, 0.176, 0.196)→(0.594, 0.174, 0.216) | (0.599, 0.177, 0.164)→(0.595, 0.165, 0.023) | 0.012→0.146 | 1.00 / 2.667 | 0.228 | 1.698 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.576
- phase_score: 0.302
- phase_breakdown.transport_arc_score: 0.011
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.392
- phase_breakdown.approach_1_score: 0.003
- grasp_place_fitness: 0.761

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.761
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.576
- **Median Q (composite search score)**: 0.034
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.341


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91282,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29421,"approach_1.approach_speed":0.16633,"descend_1.depth":0.01128,"descend_1.descend_speed":0.0749,"descend_goal.place_z_offset":0.01731,"lift_1.lift_height":0.20066,"lift_1.lift_speed":0.09911,"release_1.release_duration":1.06713,"transport_1.transport_height":0.24707,"transport_1.transport_speed":0.22809},"optimized_scores":{"best_composite_score":0.11131,"best_fitness_score":0.76131,"best_task_score":0.57638},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.58539,0.15678,-0.00726],"force_p95":1.18837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28174,"mean_force":0.45409,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5892,0.17287,0.13906]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.52672,0.02908,-0.00119],"force_p95":0.42251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60198,"mean_force":0.09502,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51493,0.02959,0.03733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.51302,0.04863,0.11692],"force_p95":0.08262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34731,"mean_force":0.05898,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51242,0.02944,0.1142]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":962.0,"contact_point_centroid":[0.59043,0.19299,0.12972],"force_p95":0.08732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32746,"mean_force":0.05272,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59348,0.17419,0.12819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20439.0,"contact_point_centroid":[0.51425,0.0105,0.11448],"force_p95":0.07783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32236,"mean_force":0.05054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51242,0.02944,0.11288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.5979,0.15578,0.12569],"force_p95":0.07933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27116,"mean_force":0.04948,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59333,0.17414,0.12797]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9703.0,"contact_point_centroid":[0.58318,0.1755,0.23878],"force_p95":0.08953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25609,"mean_force":0.05949,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58514,0.15652,0.23643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19425.0,"contact_point_centroid":[0.54525,0.06262,0.26948],"force_p95":0.08047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21132,"mean_force":0.05177,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54126,0.08115,0.26859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10089.0,"contact_point_centroid":[0.59136,0.13928,0.2306],"force_p95":0.0911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20039,"mean_force":0.05881,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58567,0.15746,0.23095]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.0308,-0.00209],"force_p95":0.14988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19702,"mean_force":0.12979,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51781,0.02979,0.03697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16747.0,"contact_point_centroid":[0.54093,0.10072,0.27155],"force_p95":0.08829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19313,"mean_force":0.05872,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54155,0.08162,0.26914]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5290.0,"contact_point_centroid":[0.5176,0.01067,0.03743],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14054,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51656,0.02971,0.03555]},{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51103,0.01336,0.3097]},{"body_a":"world","body_b":"grasp_target","contact_count":3312.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52396,0.02866,0.1801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4196.0,"contact_point_centroid":[0.51702,0.04901,0.03836],"force_p95":0.08235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08409,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51657,0.02971,0.03555]}],"total_contact_groups":15},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59675,0.16998,0.02603],"final_tcp_position":[0.59569,0.17474,0.1322],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.28174,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1688.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52461,0.02715,0.3171],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.29116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52528,0.03029,0.04558],"tcp_start":[0.52461,0.02715,0.3171],"tcp_to_object_dist_end":0.02025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.03028,0.02566],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18396,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14852,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11286.0,"raw_peak_contact_force":0.19702,"subtask_id":"grasp_1","tcp_end":[0.51653,0.02971,0.03552],"tcp_start":[0.52528,0.03029,0.04558],"tcp_to_object_dist_end":0.01706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52169,0.03015,0.17736],"object_pos_start":[0.53045,0.03028,0.02566],"object_to_goal_dist_end":0.18222,"object_to_goal_dist_start":0.18396,"object_z_max":0.17717,"peak_contact_force":0.08119,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37583.0,"raw_peak_contact_force":0.60198,"tcp_end":[0.5129,0.02947,0.19556],"tcp_start":[0.51653,0.02971,0.03552],"tcp_to_object_dist_end":0.02022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58423,0.14401,0.30508],"object_pos_start":[0.52169,0.03015,0.17736],"object_to_goal_dist_end":0.20074,"object_to_goal_dist_start":0.18222,"object_z_max":0.30497,"peak_contact_force":0.07491,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36172.0,"raw_peak_contact_force":0.21132,"subtask_id":"transport_arc","tcp_end":[0.57796,0.14175,0.32831],"tcp_start":[0.5129,0.02947,0.19556],"tcp_to_object_dist_end":0.02417,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.5948,0.17679,0.105],"object_pos_start":[0.58423,0.14401,0.30508],"object_to_goal_dist_end":0.00762,"object_to_goal_dist_start":0.20074,"object_z_max":0.30508,"peak_contact_force":0.08907,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19792.0,"raw_peak_contact_force":0.25609,"tcp_end":[0.59569,0.17474,0.1322],"tcp_start":[0.57796,0.14175,0.32831],"tcp_to_object_dist_end":0.02729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59675,0.16998,0.02603],"object_pos_start":[0.5948,0.17679,0.105],"object_to_goal_dist_end":0.08265,"object_to_goal_dist_start":0.00762,"object_z_max":0.105,"peak_contact_force":0.3427,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2398.0,"raw_peak_contact_force":1.28174,"subtask_id":"release_1","tcp_end":[0.58906,0.17282,0.15281],"tcp_start":[0.59569,0.17474,0.1322],"tcp_to_object_dist_end":0.12705,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36275,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28378,"approach_1.approach_speed":0.11742,"descend_1.depth":0.01336,"descend_1.descend_speed":0.05373,"descend_goal.place_z_offset":0.04957,"lift_1.lift_height":0.12936,"lift_1.lift_speed":0.07954,"release_1.release_duration":1.00634,"transport_1.transport_height":0.17263,"transport_1.transport_speed":0.20335},"optimized_scores":{"best_composite_score":-0.06736,"best_fitness_score":0.58264,"best_task_score":0.22369},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.57702,0.15891,-0.00796],"force_p95":1.34286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28901,"mean_force":0.39127,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57889,0.18169,0.30137]},{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.49981,-0.01528,-0.00117],"force_p95":0.31369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52336,"mean_force":0.09263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48871,-0.01531,0.04037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14933.0,"contact_point_centroid":[0.54646,0.13924,0.29369],"force_p95":0.11804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32461,"mean_force":0.06333,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55054,0.12075,0.29412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19423.0,"contact_point_centroid":[0.48718,0.00378,0.09799],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31348,"mean_force":0.04898,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48614,-0.01528,0.09611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17216.0,"contact_point_centroid":[0.48634,-0.03446,0.09839],"force_p95":0.0782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30886,"mean_force":0.05407,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48612,-0.01528,0.09565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.57208,0.19892,0.28405],"force_p95":0.20146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30206,"mean_force":0.14739,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58186,0.18284,0.28862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":355.0,"contact_point_centroid":[0.58347,0.16634,0.28184],"force_p95":0.19476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27612,"mean_force":0.11459,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58156,0.18274,0.28775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16474.0,"contact_point_centroid":[0.5554,0.10492,0.29263],"force_p95":0.09542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26671,"mean_force":0.05824,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55193,0.12346,0.29393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18005.0,"contact_point_centroid":[0.50153,0.0371,0.23189],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16813,"mean_force":0.05472,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50002,0.01804,0.2305]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01575,-0.00203],"force_p95":0.1337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15726,"mean_force":0.12549,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49159,-0.01533,0.04019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17749.0,"contact_point_centroid":[0.50331,-0.00031,0.23337],"force_p95":0.07977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14789,"mean_force":0.05563,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50033,0.0186,0.23152]},{"body_a":"world","body_b":"grasp_target","contact_count":508.0,"contact_point_centroid":[0.50382,-0.01567,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12359,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49951,-0.00527,0.30286]},{"body_a":"world","body_b":"grasp_target","contact_count":3416.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4985,-0.01312,0.17581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5086.0,"contact_point_centroid":[0.4914,0.00373,0.04059],"force_p95":0.06785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09684,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49038,-0.01532,0.03889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.4897,-0.03457,0.0414],"force_p95":0.0785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09338,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49038,-0.01532,0.03889]}],"total_contact_groups":15},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57399,0.15221,0.02665],"final_tcp_position":[0.58238,0.18285,0.29009],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.28901,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12259,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":508.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50027,-0.01089,0.30581],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3416.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49883,-0.01538,0.04804],"tcp_start":[0.50027,-0.01089,0.30581],"tcp_to_object_dist_end":0.02258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01573,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13367,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11035.0,"raw_peak_contact_force":0.15726,"subtask_id":"grasp_1","tcp_end":[0.49035,-0.01532,0.03885],"tcp_start":[0.49883,-0.01538,0.04804],"tcp_to_object_dist_end":0.01863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.49477,-0.01564,0.13837],"object_pos_start":[0.5037,-0.01573,0.02587],"object_to_goal_dist_end":0.24855,"object_to_goal_dist_start":0.31241,"object_z_max":0.13828,"peak_contact_force":0.07953,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36796.0,"raw_peak_contact_force":0.52336,"tcp_end":[0.48648,-0.01527,0.15756],"tcp_start":[0.49035,-0.01532,0.03885],"tcp_to_object_dist_end":0.0209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53006,0.06183,0.27864],"object_pos_start":[0.49477,-0.01564,0.13837],"object_to_goal_dist_end":0.14122,"object_to_goal_dist_start":0.24855,"object_z_max":0.27853,"peak_contact_force":0.08531,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35754.0,"raw_peak_contact_force":0.16813,"subtask_id":"transport_arc","tcp_end":[0.52187,0.0609,0.30337],"tcp_start":[0.48648,-0.01527,0.15756],"tcp_to_object_dist_end":0.02606,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.57811,0.18266,0.25598],"object_pos_start":[0.53006,0.06183,0.27864],"object_to_goal_dist_end":0.01273,"object_to_goal_dist_start":0.14122,"object_z_max":0.27867,"peak_contact_force":0.15134,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31407.0,"raw_peak_contact_force":0.32461,"tcp_end":[0.58238,0.18285,0.29009],"tcp_start":[0.52187,0.0609,0.30337],"tcp_to_object_dist_end":0.03437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57399,0.15221,0.02665],"object_pos_start":[0.57811,0.18266,0.25598],"object_to_goal_dist_end":0.22463,"object_to_goal_dist_start":0.01273,"object_z_max":0.25598,"peak_contact_force":0.23041,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":738.0,"raw_peak_contact_force":2.28901,"subtask_id":"release_1","tcp_end":[0.57886,0.18169,0.31141],"tcp_start":[0.58238,0.18285,0.29009],"tcp_to_object_dist_end":0.28632,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94964,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22588,"approach_1.approach_speed":0.13599,"descend_1.depth":0.01001,"descend_1.descend_speed":0.11363,"descend_goal.place_z_offset":0.01202,"lift_1.lift_height":0.20212,"lift_1.lift_speed":0.13322,"release_1.release_duration":0.78399,"transport_1.transport_height":0.14457,"transport_1.transport_speed":0.23441},"optimized_scores":{"best_composite_score":0.03385,"best_fitness_score":0.68385,"best_task_score":0.41998},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":227.0,"contact_point_centroid":[0.6108,0.17528,-0.00543],"force_p95":1.1864,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52389,"mean_force":0.33177,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61562,0.16788,0.17516]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.50972,0.0381,-0.00128],"force_p95":0.32986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59419,"mean_force":0.09237,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49708,0.0381,0.03663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":775.0,"contact_point_centroid":[0.61788,0.18839,0.1571],"force_p95":0.19807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43235,"mean_force":0.0888,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61939,0.16901,0.15962]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14073.0,"contact_point_centroid":[0.55964,0.0805,0.26185],"force_p95":0.09546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38711,"mean_force":0.07109,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55255,0.09826,0.26194]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3888.0,"contact_point_centroid":[0.61357,0.18211,0.22129],"force_p95":0.11971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3575,"mean_force":0.0823,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61532,0.16316,0.22333]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":727.0,"contact_point_centroid":[0.62601,0.15193,0.15499],"force_p95":0.10225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34664,"mean_force":0.06762,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61964,0.16908,0.16003]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11825.0,"contact_point_centroid":[0.49756,0.05706,0.11801],"force_p95":0.10973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33845,"mean_force":0.07592,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49485,0.03793,0.11562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12710.0,"contact_point_centroid":[0.5558,0.11928,0.26418],"force_p95":0.10941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33201,"mean_force":0.07655,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55444,0.10017,0.26307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14441.0,"contact_point_centroid":[0.49891,0.01944,0.11377],"force_p95":0.10225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.314,"mean_force":0.06416,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49483,0.03792,0.11257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4127.0,"contact_point_centroid":[0.62156,0.14561,0.22022],"force_p95":0.11488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25884,"mean_force":0.07922,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61522,0.16305,0.2244]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03969,-0.00213],"force_p95":0.15855,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21075,"mean_force":0.13209,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50005,0.03835,0.0362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.50044,0.01924,0.03634],"force_p95":0.07373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1778,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49882,0.03825,0.03486]},{"body_a":"world","body_b":"grasp_target","contact_count":808.0,"contact_point_centroid":[0.51251,0.03972,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50334,0.0171,0.28249]},{"body_a":"world","body_b":"grasp_target","contact_count":2612.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50645,0.03605,0.15197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4220.0,"contact_point_centroid":[0.49903,0.05755,0.03756],"force_p95":0.08392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08952,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49882,0.03825,0.03487]}],"total_contact_groups":15},"final_pose_error":0.00979,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61316,0.17229,0.01569],"final_tcp_position":[0.62169,0.16961,0.16431],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.52389,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":808.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50775,0.03332,0.26169],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2612.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50738,0.03894,0.04431],"tcp_start":[0.50775,0.03332,0.26169],"tcp_to_object_dist_end":0.01901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03892,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21299,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15617,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11052.0,"raw_peak_contact_force":0.21075,"subtask_id":"grasp_1","tcp_end":[0.49879,0.03825,0.03483],"tcp_start":[0.50738,0.03894,0.04431],"tcp_to_object_dist_end":0.01657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":902.0,"n_steps_budget":960.0,"object_pos_end":[0.50748,0.03909,0.19994],"object_pos_start":[0.5125,0.03892,0.02556],"object_to_goal_dist_end":0.18773,"object_to_goal_dist_start":0.21299,"object_z_max":0.19979,"peak_contact_force":0.1089,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26428.0,"raw_peak_contact_force":0.59419,"tcp_end":[0.49563,0.03799,0.22269],"tcp_start":[0.49879,0.03825,0.03483],"tcp_to_object_dist_end":0.02567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61372,0.15957,0.2503],"object_pos_start":[0.50748,0.03909,0.19994],"object_to_goal_dist_end":0.10696,"object_to_goal_dist_start":0.18773,"object_z_max":0.25123,"peak_contact_force":0.09786,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26783.0,"raw_peak_contact_force":0.38711,"subtask_id":"transport_arc","tcp_end":[0.61122,0.15771,0.28166],"tcp_start":[0.49563,0.03799,0.22269],"tcp_to_object_dist_end":0.03152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.6232,0.17196,0.13075],"object_pos_start":[0.61372,0.15957,0.2503],"object_to_goal_dist_end":0.01494,"object_to_goal_dist_start":0.10696,"object_z_max":0.2503,"peak_contact_force":0.12218,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8015.0,"raw_peak_contact_force":0.3575,"tcp_end":[0.62169,0.16961,0.16431],"tcp_start":[0.61122,0.15771,0.28166],"tcp_to_object_dist_end":0.03368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61316,0.17229,0.01569],"object_pos_start":[0.6232,0.17196,0.13075],"object_to_goal_dist_end":0.13013,"object_to_goal_dist_start":0.01494,"object_z_max":0.13075,"peak_contact_force":0.11061,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1729.0,"raw_peak_contact_force":1.52389,"subtask_id":"release_1","tcp_end":[0.61556,0.16787,0.18399],"tcp_start":[0.62169,0.16961,0.16431],"tcp_to_object_dist_end":0.16837,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```