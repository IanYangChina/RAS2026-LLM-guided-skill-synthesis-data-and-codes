## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.1672 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0796 | 0.39 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1519 | 0.35 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0222 | 0.51 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1191 | 0.41 | ✅ accepted |

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

## Current Skill (Q=0.167) — your mutation base

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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
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
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
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
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: scale
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.001
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_retained
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: abort
  subtask_id: transport_arc
- id: place_descend
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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.001
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
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
  parameters:
    release_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (scale)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.001
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_retained, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.001
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (add)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.167
- **task_score** (E): 0.291
- **fitness_score**: 0.620  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.048
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1016 |
| descend_1 | 1.00 | 1.00 | 0.1780 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1299 |
| transport_approach | 0.00 | 1.00 | 0.1441 |
| place_descend | 1.00 | 1.00 | 0.0238 |
| release_1 | 1.00 | 1.00 | 0.0152 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.016, 0.204) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.016, 0.204)→(0.511, 0.018, 0.026) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.333 | 0.158 | 0.158 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.026)→(0.502, 0.018, 0.017) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.025) | 0.236→0.237 | 1.00 / 37.000 | 0.255 | 0.413 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.018, 0.017)→(0.510, 0.018, 0.147) | (0.515, 0.018, 0.025)→(0.529, 0.018, 0.136) | 0.237→0.186 | 1.00 / 20.667 | 0.198 | 1.343 |
| transport_approach | approach | 0.00 / step_budget | (0.510, 0.018, 0.147)→(0.575, 0.090, 0.168) | (0.529, 0.018, 0.136)→(0.543, 0.045, 0.050) | 0.186→0.207 | 1.00 / 13.667 | 90995.649 | 868.248 |
| place_descend | descend | 1.00 / force_exceeded | (0.524, 0.030, 0.118)→(0.536, 0.051, 0.114) | (0.549, 0.031, 0.118)→(0.561, 0.047, 0.113) | 0.157→0.138 | 1.00 / 15.000 | 16.410 | 0.283 |
| release_1 | release | 1.00 / step_budget | (0.536, 0.051, 0.114)→(0.530, 0.058, 0.126) | (0.561, 0.047, 0.113)→(0.566, 0.086, 0.016) | 0.138→0.135 | 1.00 / 4.000 | 0.124 | 1.366 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.406
- phase_score: 0.229
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.059
- phase_breakdown.transport_arc_score: 0.035
- phase_breakdown.approach_1_score: 0.049
- phase_breakdown.descend_1_score: 0.485
- grasp_place_fitness: 0.669

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.669
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.406
- **Median Q (composite search score)**: 0.141
- **K-run variance**: 0.0118
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.233


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":52.0,"average_failure_rate":0.36111,"average_mean_iterations":74.80556,"average_solve_count":144.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14404,"descend_1.grasp_z_offset":-0.01994,"lift_1.lift_distance":0.10717,"place_descend.place_force_threshold":9.49254,"release_1.release_time":1.59017,"transport_approach.transport_height":0.13076,"transport_approach.transport_speed":0.21671},"optimized_scores":{"best_composite_score":0.31149,"best_fitness_score":0.66863,"best_task_score":0.40595},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":148.0,"contact_point_centroid":[0.51884,0.06754,-0.00048],"force_p95":2.4276,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.61078,"mean_force":0.75339,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51644,0.02961,0.00584]},{"body_a":"world","body_b":"left_finger","contact_count":129.0,"contact_point_centroid":[0.51915,-0.00834,-0.00044],"force_p95":2.43672,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.59812,"mean_force":0.75772,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51648,0.02962,0.00573]},{"body_a":"world","body_b":"grasp_target","contact_count":520.0,"contact_point_centroid":[0.56629,0.08586,-0.00333],"force_p95":0.7762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36574,"mean_force":0.19984,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53076,0.0578,0.10902]},{"body_a":"grasp_target","body_b":"hand","contact_count":450.0,"contact_point_centroid":[0.53526,0.03196,0.049],"force_p95":0.33619,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.81405,"mean_force":0.31854,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51798,0.02972,0.00644]},{"body_a":"world","body_b":"grasp_target","contact_count":388.0,"contact_point_centroid":[0.52923,0.03035,-0.00228],"force_p95":0.26387,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75185,"mean_force":0.14008,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51497,0.02955,0.01137]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.54696,0.04118,0.11076],"force_p95":0.28434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72462,"mean_force":0.14899,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54202,0.06097,0.11059]},{"body_a":"world","body_b":"right_finger","contact_count":3932.0,"contact_point_centroid":[0.51706,0.06905,-0.00058],"force_p95":0.48242,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.58161,"mean_force":0.30438,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51702,0.02966,0.00539]},{"body_a":"world","body_b":"left_finger","contact_count":3699.0,"contact_point_centroid":[0.51753,-0.00969,-0.00051],"force_p95":0.4432,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.46531,"mean_force":0.27273,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51701,0.02966,0.00537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":266.0,"contact_point_centroid":[0.5484,0.0833,0.10281],"force_p95":0.36427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43401,"mean_force":0.20502,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54112,0.06428,0.10311]},{"body_a":"grasp_target","body_b":"hand","contact_count":682.0,"contact_point_centroid":[0.53052,0.03341,0.09674],"force_p95":0.2155,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41675,"mean_force":0.1308,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51809,0.02984,0.05725]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5296,0.03067,-0.00318],"force_p95":0.24654,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34088,"mean_force":0.20075,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51798,0.02972,0.00644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.5337,0.01768,0.11837],"force_p95":0.27005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28329,"mean_force":0.2288,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.52812,0.03673,0.11724]},{"body_a":"grasp_target","body_b":"hand","contact_count":12.0,"contact_point_centroid":[0.54175,0.04084,0.05508],"force_p95":0.22766,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22979,"mean_force":0.19783,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52506,0.03017,0.01623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9216.0,"contact_point_centroid":[0.52142,0.01101,0.0623],"force_p95":0.10437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22007,"mean_force":0.07137,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51816,0.02986,0.06003]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10161.0,"contact_point_centroid":[0.52114,0.04861,0.0596],"force_p95":0.10163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21231,"mean_force":0.06742,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51797,0.02984,0.05803]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18041,"mean_force":0.12341,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52314,0.02878,0.09646]}],"total_contact_groups":18},"final_pose_error":0.14372,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56601,0.08614,0.016],"final_tcp_position":[0.53627,0.05069,0.11444],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":16.40987,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52395,0.02753,0.18062],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.53037,0.03083,0.02565],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18355,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.22979,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.22979,"subtask_id":"descend_1","tcp_end":[0.52504,0.03019,0.01425],"tcp_start":[0.52395,0.02753,0.18062],"tcp_to_object_dist_end":0.0126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52931,0.03073,0.02345],"object_pos_start":[0.53037,0.03083,0.02565],"object_to_goal_dist_end":0.18504,"object_to_goal_dist_start":0.18355,"object_z_max":0.02565,"peak_contact_force":0.48231,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9881.0,"raw_peak_contact_force":0.81405,"subtask_id":"grasp_1","tcp_end":[0.5168,0.02965,0.00519],"tcp_start":[0.52504,0.03019,0.01425],"tcp_to_object_dist_end":0.02217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.54876,0.0306,0.11835],"object_pos_start":[0.52931,0.03073,0.02345],"object_to_goal_dist_end":0.15744,"object_to_goal_dist_start":0.18504,"object_z_max":0.11827,"peak_contact_force":0.12316,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20724.0,"raw_peak_contact_force":2.61078,"tcp_end":[0.52438,0.03039,0.1182],"tcp_start":[0.5168,0.02965,0.00519],"tcp_to_object_dist_end":0.02439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.54876,0.0306,0.11835],"object_pos_start":[0.54876,0.0306,0.11835],"object_to_goal_dist_end":0.15744,"object_to_goal_dist_start":0.15744,"peak_contact_force":0.1234,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"transport_arc","tcp_end":[0.52438,0.03039,0.1182],"tcp_start":[0.52438,0.03039,0.1182],"tcp_to_object_dist_end":0.02439,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.56091,0.04686,0.11345],"object_pos_start":[0.54876,0.0306,0.11835],"object_to_goal_dist_end":0.13795,"object_to_goal_dist_start":0.15744,"object_z_max":0.11837,"peak_contact_force":16.40987,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":308.0,"raw_peak_contact_force":0.28329,"subtask_id":"release_1","tcp_end":[0.53627,0.05069,0.11444],"tcp_start":[0.52438,0.03039,0.1182],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56601,0.08614,0.016],"object_pos_start":[0.56091,0.04686,0.11345],"object_to_goal_dist_end":0.13523,"object_to_goal_dist_start":0.13795,"object_z_max":0.11345,"peak_contact_force":0.12352,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":937.0,"raw_peak_contact_force":1.36574,"tcp_end":[0.53008,0.05783,0.12629],"tcp_start":[0.53627,0.05069,0.11444],"tcp_to_object_dist_end":0.1194,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.7069,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17211,"descend_1.grasp_z_offset":-0.0017,"lift_1.lift_distance":0.19348,"place_descend.place_force_threshold":4.79708,"release_1.release_time":0.90268,"transport_approach.transport_height":0.22337,"transport_approach.transport_speed":0.35417},"optimized_scores":{"best_composite_score":0.04914,"best_fitness_score":0.54914,"best_task_score":0.13979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":66.0,"contact_point_centroid":[0.55121,-0.05854,-0.00373],"force_p95":766.49999,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":925.2306,"mean_force":252.4253,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50383,-0.00678,-0.01046]},{"body_a":"world","body_b":"link7","contact_count":201.0,"contact_point_centroid":[0.6042,0.01021,-9e-05],"force_p95":333.9778,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":371.27487,"mean_force":193.39311,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.47936,0.00069,0.01123]},{"body_a":"world","body_b":"link6","contact_count":345.0,"contact_point_centroid":[0.66389,0.06111,-0.00018],"force_p95":241.13679,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.76472,"mean_force":214.28024,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.42473,0.03596,0.06612]},{"body_a":"world","body_b":"right_finger","contact_count":2037.0,"contact_point_centroid":[0.49963,0.00661,-0.00542],"force_p95":8.38004,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.49763,"mean_force":3.41948,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.49787,-0.00585,-0.00248]},{"body_a":"world","body_b":"left_finger","contact_count":2070.0,"contact_point_centroid":[0.5015,-0.01792,-0.00539],"force_p95":8.27059,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.203,"mean_force":3.33603,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.49769,-0.00582,-0.00235]},{"body_a":"grasp_target","body_b":"hand","contact_count":603.0,"contact_point_centroid":[0.54135,-0.004,0.02563],"force_p95":1.75137,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.54889,"mean_force":0.87712,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.45271,0.01808,0.03729]},{"body_a":"world","body_b":"grasp_target","contact_count":3387.0,"contact_point_centroid":[0.52884,0.01241,-0.00568],"force_p95":0.78869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.66246,"mean_force":0.37031,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.44526,0.04188,0.09384]},{"body_a":"grasp_target","body_b":"link7","contact_count":492.0,"contact_point_centroid":[0.55037,0.01083,0.02412],"force_p95":1.1664,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.15467,"mean_force":0.55691,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.43143,0.03259,0.06187]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":520.0,"contact_point_centroid":[0.53736,-0.0279,0.15863],"force_p95":0.57393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.15791,"mean_force":0.23202,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.53672,-0.01263,0.16342]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":326.0,"contact_point_centroid":[0.53343,0.00332,0.1486],"force_p95":0.32717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72942,"mean_force":0.16863,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.53272,-0.01289,0.1546]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.50164,-0.0151,-0.00109],"force_p95":0.51282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68314,"mean_force":0.07593,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48948,-0.01532,0.02607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14125.0,"contact_point_centroid":[0.49428,0.00353,0.09472],"force_p95":0.13191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31715,"mean_force":0.07274,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49161,-0.01523,0.09408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14620.0,"contact_point_centroid":[0.49432,-0.03396,0.09259],"force_p95":0.12869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29193,"mean_force":0.07065,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4915,-0.01523,0.09213]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01551,-0.00203],"force_p95":0.13243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16365,"mean_force":0.12549,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49197,-0.01536,0.02556]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49927,-0.00634,0.25612]},{"body_a":"world","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49828,-0.01434,0.121]}],"total_contact_groups":19},"final_pose_error":0.26885,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51653,0.01926,0.01602],"final_tcp_position":[0.43828,0.11664,0.25894],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":925.2306,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50011,-0.01331,0.21106],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.499,-0.01544,0.033],"tcp_start":[0.50011,-0.01331,0.21106],"tcp_to_object_dist_end":0.00848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.0152,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31207,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12997,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10799.0,"raw_peak_contact_force":0.16365,"subtask_id":"grasp_1","tcp_end":[0.49077,-0.01534,0.0243],"tcp_start":[0.499,-0.01544,0.033],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51132,-0.01512,0.16257],"object_pos_start":[0.50367,-0.0152,0.02588],"object_to_goal_dist_end":0.23252,"object_to_goal_dist_start":0.31207,"object_z_max":0.16242,"peak_contact_force":0.34755,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28880.0,"raw_peak_contact_force":0.68314,"tcp_end":[0.49795,-0.01516,0.18409],"tcp_start":[0.49077,-0.01534,0.0243],"tcp_to_object_dist_end":0.02533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51653,0.01926,0.01602],"object_pos_start":[0.51132,-0.01512,0.16257],"object_to_goal_dist_end":0.29514,"object_to_goal_dist_start":0.23252,"object_z_max":0.1628,"peak_contact_force":0.12265,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12637.0,"raw_peak_contact_force":925.2306,"subtask_id":"transport_arc","tcp_end":[0.43828,0.11664,0.25894],"tcp_start":[0.49795,-0.01516,0.18409],"tcp_to_object_dist_end":0.27316,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.6729,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18322,"descend_1.grasp_z_offset":-0.0043,"lift_1.lift_distance":0.124,"place_descend.place_force_threshold":5.402,"release_1.release_time":1.31034,"transport_approach.transport_height":0.18648,"transport_approach.transport_speed":0.36588},"optimized_scores":{"best_composite_score":0.14093,"best_fitness_score":0.64093,"best_task_score":0.32612},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":414.0,"contact_point_centroid":[0.66712,0.07816,-0.00046],"force_p95":253.43186,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1679.51296,"mean_force":93.51724,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.72435,0.10713,0.12342]},{"body_a":"world","body_b":"link6","contact_count":871.0,"contact_point_centroid":[0.57486,-0.07451,-0.00026],"force_p95":330.05862,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1151.97773,"mean_force":242.07475,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.72824,0.10347,0.13462]},{"body_a":"world","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.56649,-0.01749,-0.0008],"force_p95":400.66818,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":667.7803,"mean_force":74.19781,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.53368,0.12169,0.04867]},{"body_a":"world","body_b":"right_finger","contact_count":281.0,"contact_point_centroid":[0.5222,0.10196,-0.00686],"force_p95":29.38615,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.96594,"mean_force":11.60932,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50819,0.09696,-0.00387]},{"body_a":"world","body_b":"left_finger","contact_count":205.0,"contact_point_centroid":[0.49288,0.0859,-0.00474],"force_p95":36.38964,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.06054,"mean_force":14.80445,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50757,0.09491,-0.00664]},{"body_a":"grasp_target","body_b":"hand","contact_count":63.0,"contact_point_centroid":[0.54727,0.04746,0.02844],"force_p95":3.21976,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.87094,"mean_force":1.3918,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.52214,0.10347,0.02402]},{"body_a":"grasp_target","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54266,0.01221,0.02803],"force_p95":2.58077,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.70587,"mean_force":1.55019,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.5284,0.11877,0.04017]},{"body_a":"world","body_b":"grasp_target","contact_count":3622.0,"contact_point_centroid":[0.56007,0.08242,-0.00277],"force_p95":0.44985,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29742,"mean_force":0.17084,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.72034,0.10377,0.12749]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.51048,0.03722,-0.00119],"force_p95":0.56395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7339,"mean_force":0.0816,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49795,0.03811,0.02304]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":394.0,"contact_point_centroid":[0.53128,0.0558,0.12469],"force_p95":0.36619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60729,"mean_force":0.18399,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.52401,0.03866,0.12593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":487.0,"contact_point_centroid":[0.52664,0.02046,0.11578],"force_p95":0.37257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54327,"mean_force":0.1587,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.5259,0.03965,0.11876]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11370.0,"contact_point_centroid":[0.50345,0.05674,0.07306],"force_p95":0.10639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30429,"mean_force":0.06663,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50069,0.03787,0.07159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11118.0,"contact_point_centroid":[0.50355,0.019,0.07622],"force_p95":0.10819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2941,"mean_force":0.06744,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50098,0.03786,0.0747]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03932,-0.00213],"force_p95":0.16314,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25987,"mean_force":0.13371,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50042,0.03835,0.0224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4038.0,"contact_point_centroid":[0.49986,0.01906,0.02392],"force_p95":0.08121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14091,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49922,0.03826,0.02112]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50288,0.01635,0.2598]}],"total_contact_groups":19},"final_pose_error":0.2497,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.56311,0.0862,0.01602],"final_tcp_position":[0.76329,0.12196,0.12811],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":272986.70118,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50765,0.03398,0.21961],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2340.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50755,0.03894,0.0301],"tcp_start":[0.50765,0.03398,0.21961],"tcp_to_object_dist_end":0.00647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51236,0.03815,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21354,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15349,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10844.0,"raw_peak_contact_force":0.25987,"subtask_id":"grasp_1","tcp_end":[0.4992,0.03825,0.02109],"tcp_start":[0.50755,0.03894,0.0301],"tcp_to_object_dist_end":0.0139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.52769,0.03801,0.12818],"object_pos_start":[0.51236,0.03815,0.02556],"object_to_goal_dist_end":0.16838,"object_to_goal_dist_start":0.21354,"object_z_max":0.12808,"peak_contact_force":0.12245,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22634.0,"raw_peak_contact_force":0.7339,"tcp_end":[0.50765,0.03784,0.13728],"tcp_start":[0.4992,0.03825,0.02109],"tcp_to_object_dist_end":0.02202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56311,0.0862,0.01602],"object_pos_start":[0.52769,0.03801,0.12818],"object_to_goal_dist_end":0.16807,"object_to_goal_dist_start":0.16838,"object_z_max":0.12822,"peak_contact_force":272986.70118,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9964.0,"raw_peak_contact_force":1679.51296,"subtask_id":"transport_arc","tcp_end":[0.76329,0.12196,0.12811],"tcp_start":[0.50765,0.03784,0.13728],"tcp_to_object_dist_end":0.2322,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```