## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1449 | 0.36 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1025 | 0.26 | ❌ rejected |
| 12 | approach → descend → grasp → lift → retract → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1121 | 0.38 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.1672 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0796 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.145) — your mutation base

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

- **Composite score**: -0.145
- **task_score** (E): 0.356
- **fitness_score**: 0.405  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1059 |
| descend_1 | 1.00 | 1.00 | 0.1591 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.0133 |
| transport_arc | 0.67 | 1.00 | 0.2209 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.200) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.016, 0.200)→(0.511, 0.018, 0.041) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.041)→(0.502, 0.018, 0.031) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.144 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.509, 0.017, 0.036)→(0.514, 0.017, 0.047) | (0.516, 0.018, 0.026)→(0.521, 0.017, 0.028) | 0.237→0.233 | 1.00 / 37.667 | 0.081 | 0.377 |
| transport_arc | approach | 0.67 / step_budget | (0.514, 0.017, 0.047)→(0.584, 0.145, 0.210) | (0.525, 0.017, 0.038)→(0.568, 0.105, 0.016) | 0.226→0.176 | 1.00 / 8.333 | 91002.682 | 1.568 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 1.000
- terminal_score: 0.528
- phase_score: 0.423
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.transport_arc_score: 0.340
- phase_breakdown.approach_1_score: 0.026
- phase_breakdown.descend_1_score: 0.852
- grasp_place_fitness: 0.489

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.489
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.528
- **Median Q (composite search score)**: -0.123
- **K-run variance**: 0.0062
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39831,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17632,"descend_1.grasp_z_offset":0.00952,"lift_1.lift_distance":0.11876,"lift_1.lift_speed":0.22322,"place_descend.place_z_offset":-0.00291,"release_1.release_time":1.40089,"transport_arc.arc_height":0.23967,"transport_arc.transport_speed":0.28953},"optimized_scores":{"best_composite_score":-0.06134,"best_fitness_score":0.48866,"best_task_score":0.52812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":493.0,"contact_point_centroid":[0.58433,0.13586,-0.00346],"force_p95":0.78049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32181,"mean_force":0.20152,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5733,0.12696,0.13599]},{"body_a":"world","body_b":"grasp_target","contact_count":1442.0,"contact_point_centroid":[0.53613,0.02939,-0.00246],"force_p95":0.25155,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31476,"mean_force":0.1615,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52297,0.02922,0.03484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10158.0,"contact_point_centroid":[0.54307,0.07722,0.0948],"force_p95":0.12987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31081,"mean_force":0.07851,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53927,0.05854,0.09403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10275.0,"contact_point_centroid":[0.54144,0.03704,0.0909],"force_p95":0.13549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27851,"mean_force":0.07683,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5379,0.05568,0.09013]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03057,-0.00211],"force_p95":0.15347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22086,"mean_force":0.13087,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51812,0.02968,0.0357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8284.0,"contact_point_centroid":[0.52412,0.04822,0.03719],"force_p95":0.07772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19768,"mean_force":0.05187,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52353,0.0292,0.03535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7219.0,"contact_point_centroid":[0.52426,0.01007,0.03816],"force_p95":0.0809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17351,"mean_force":0.05675,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52365,0.0292,0.03546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.51762,0.0104,0.03711],"force_p95":0.07976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14444,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51691,0.0296,0.03433]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51059,0.013,0.25569]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52312,0.02839,0.12712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.5176,0.04874,0.03614],"force_p95":0.07235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08247,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51691,0.0296,0.03434]},{"body_a":"left_finger","body_b":"right_finger","contact_count":144.0,"contact_point_centroid":[0.58485,0.14985,0.15452],"force_p95":0.01528,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01574,"mean_force":0.01225,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58407,0.14984,0.15251]}],"total_contact_groups":12},"final_pose_error":0.031,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5897,0.15448,0.01617],"final_tcp_position":[0.58566,0.15252,0.15263],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.32181,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1276.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52347,0.02678,0.21202],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52531,0.03016,0.04397],"tcp_start":[0.52347,0.02678,0.21202],"tcp_to_object_dist_end":0.0187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02968,0.02564],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18447,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14732,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10851.0,"raw_peak_contact_force":0.22086,"subtask_id":"grasp_1","tcp_end":[0.51688,0.0296,0.0343],"tcp_start":[0.52531,0.03016,0.04397],"tcp_to_object_dist_end":0.01607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":419.0,"n_steps_budget":600.0,"object_pos_end":[0.5352,0.02937,0.02384],"object_pos_start":[0.53041,0.02968,0.02564],"object_to_goal_dist_end":0.18374,"object_to_goal_dist_start":0.18447,"object_z_max":0.03,"peak_contact_force":0.08215,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16945.0,"raw_peak_contact_force":0.31476,"tcp_end":[0.52877,0.02903,0.04047],"tcp_start":[0.52293,0.02935,0.03331],"tcp_to_object_dist_end":0.01783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5897,0.15448,0.01617],"object_pos_start":[0.5399,0.02916,0.03002],"object_to_goal_dist_end":0.09576,"object_to_goal_dist_start":0.1795,"object_z_max":0.12195,"peak_contact_force":0.12759,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21070.0,"raw_peak_contact_force":1.32181,"subtask_id":"transport_arc","tcp_end":[0.58566,0.15252,0.15263],"tcp_start":[0.52877,0.02903,0.04047],"tcp_to_object_dist_end":0.13654,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58475,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1456,"descend_1.grasp_z_offset":0.00338,"lift_1.lift_distance":0.13349,"lift_1.lift_speed":0.29236,"place_descend.place_z_offset":-0.01117,"release_1.release_time":1.3486,"transport_arc.arc_height":0.29676,"transport_arc.transport_speed":0.39586},"optimized_scores":{"best_composite_score":-0.25036,"best_fitness_score":0.29964,"best_task_score":0.1418},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2037.0,"contact_point_centroid":[0.52325,0.01978,-0.00246],"force_p95":0.16895,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69868,"mean_force":0.15009,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53219,0.06169,0.25641]},{"body_a":"world","body_b":"grasp_target","contact_count":819.0,"contact_point_centroid":[0.51027,-0.01519,-0.00136],"force_p95":0.22118,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42739,"mean_force":0.09944,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49364,-0.01523,0.03193]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5452.0,"contact_point_centroid":[0.50025,-0.03836,0.0929],"force_p95":0.13473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32136,"mean_force":0.0729,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49713,-0.01953,0.09184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5354.0,"contact_point_centroid":[0.5003,-0.00063,0.09486],"force_p95":0.13268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32063,"mean_force":0.07438,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49715,-0.01947,0.0936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9100.0,"contact_point_centroid":[0.49689,-0.03427,0.03926],"force_p95":0.07785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19195,"mean_force":0.05412,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49655,-0.01519,0.03697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8977.0,"contact_point_centroid":[0.49703,0.0039,0.03956],"force_p95":0.07849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17695,"mean_force":0.05457,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49668,-0.01519,0.03716]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01553,-0.00203],"force_p95":0.13271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15994,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49199,-0.01537,0.03053]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49911,-0.00666,0.24263]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49817,-0.0146,0.11053]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.4913,0.00385,0.03207],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11694,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49083,-0.01535,0.02931]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.49136,-0.03443,0.03115],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08979,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49083,-0.01535,0.02931]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1983.0,"contact_point_centroid":[0.53461,0.06669,0.2635],"force_p95":0.0115,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53433,0.06669,0.26113]}],"total_contact_groups":12},"final_pose_error":0.05771,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52299,0.02044,0.01602],"final_tcp_position":[0.56325,0.13524,0.2915],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.69868,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49998,-0.01381,0.18442],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49897,-0.01545,0.03798],"tcp_start":[0.49998,-0.01381,0.18442],"tcp_to_object_dist_end":0.0129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01522,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13039,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15994,"subtask_id":"grasp_1","tcp_end":[0.4908,-0.01535,0.02927],"tcp_start":[0.49897,-0.01545,0.03798],"tcp_to_object_dist_end":0.01333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":479.0,"n_steps_budget":600.0,"object_pos_end":[0.50877,-0.01522,0.02973],"object_pos_start":[0.50369,-0.01522,0.02587],"object_to_goal_dist_end":0.30802,"object_to_goal_dist_start":0.31208,"object_z_max":0.04041,"peak_contact_force":0.08096,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18896.0,"raw_peak_contact_force":0.42739,"tcp_end":[0.50259,-0.01516,0.04792],"tcp_start":[0.49681,-0.01518,0.03468],"tcp_to_object_dist_end":0.01922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52299,0.02044,0.01602],"object_pos_start":[0.51342,-0.01514,0.04044],"object_to_goal_dist_end":0.293,"object_to_goal_dist_start":0.29929,"object_z_max":0.1472,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14826.0,"raw_peak_contact_force":1.69868,"subtask_id":"transport_arc","tcp_end":[0.56325,0.13524,0.2915],"tcp_start":[0.50259,-0.01516,0.04792],"tcp_to_object_dist_end":0.30114,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48305,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16558,"descend_1.grasp_z_offset":0.00539,"lift_1.lift_distance":0.17071,"lift_1.lift_speed":0.25582,"place_descend.place_z_offset":0.00111,"release_1.release_time":1.1889,"transport_arc.arc_height":0.29884,"transport_arc.transport_speed":0.29078},"optimized_scores":{"best_composite_score":-0.12306,"best_fitness_score":0.42694,"best_task_score":0.39879},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":588.0,"contact_point_centroid":[0.59108,0.13864,-0.00358],"force_p95":0.94294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68309,"mean_force":0.21606,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59289,0.1354,0.18249]},{"body_a":"world","body_b":"grasp_target","contact_count":799.0,"contact_point_centroid":[0.51937,0.03789,-0.00124],"force_p95":0.22504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39016,"mean_force":0.08867,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50188,0.038,0.03407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9970.0,"contact_point_centroid":[0.52915,0.03953,0.1057],"force_p95":0.13254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31106,"mean_force":0.07284,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52601,0.05822,0.1049]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9732.0,"contact_point_centroid":[0.53226,0.07991,0.11101],"force_p95":0.1206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29644,"mean_force":0.07546,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52855,0.06117,0.11007]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03944,-0.00213],"force_p95":0.16107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23808,"mean_force":0.13286,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50055,0.03836,0.03218]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11130.0,"contact_point_centroid":[0.50582,0.05682,0.04303],"force_p95":0.07892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18171,"mean_force":0.05316,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50542,0.03776,0.04098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10249.0,"contact_point_centroid":[0.50615,0.01864,0.04414],"force_p95":0.08228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17538,"mean_force":0.05569,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50567,0.03775,0.04154]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4065.0,"contact_point_centroid":[0.49993,0.01906,0.0337],"force_p95":0.08091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1494,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49937,0.03827,0.0309]},{"body_a":"world","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50288,0.01677,0.25121]},{"body_a":"world","body_b":"grasp_target","contact_count":2012.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50637,0.03671,0.12045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5002.0,"contact_point_centroid":[0.49992,0.05743,0.03273],"force_p95":0.07361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08329,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49937,0.03827,0.03091]},{"body_a":"left_finger","body_b":"right_finger","contact_count":416.0,"contact_point_centroid":[0.59676,0.1395,0.18604],"force_p95":0.01408,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01122,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59642,0.13948,0.18372]}],"total_contact_groups":12},"final_pose_error":0.03701,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59085,0.14055,0.01601],"final_tcp_position":[0.60267,0.14693,0.18528],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273007.79539,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1324.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50772,0.03468,0.20253],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50758,0.03893,0.03991],"tcp_start":[0.50772,0.03468,0.20253],"tcp_to_object_dist_end":0.01476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03834,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2134,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15298,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10867.0,"raw_peak_contact_force":0.23808,"subtask_id":"grasp_1","tcp_end":[0.49934,0.03826,0.03087],"tcp_start":[0.50758,0.03893,0.03991],"tcp_to_object_dist_end":0.01412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":570.0,"n_steps_budget":600.0,"object_pos_end":[0.51766,0.03791,0.03132],"object_pos_start":[0.51242,0.03834,0.02555],"object_to_goal_dist_end":0.20768,"object_to_goal_dist_start":0.2134,"object_z_max":0.0436,"peak_contact_force":0.0792,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22178.0,"raw_peak_contact_force":0.39016,"tcp_end":[0.51166,0.03753,0.05385],"tcp_start":[0.50582,0.03793,0.03858],"tcp_to_object_dist_end":0.02332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59085,0.14055,0.01601],"object_pos_start":[0.52184,0.03764,0.04362],"object_to_goal_dist_end":0.1379,"object_to_goal_dist_start":0.19914,"object_z_max":0.14666,"peak_contact_force":273007.79539,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20706.0,"raw_peak_contact_force":1.68309,"subtask_id":"transport_arc","tcp_end":[0.60267,0.14693,0.18528],"tcp_start":[0.51166,0.03753,0.05385],"tcp_to_object_dist_end":0.1698,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```